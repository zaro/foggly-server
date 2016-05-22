from celery import shared_task
from core.models import SharedDatabase, DomainModel, DockerContainer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import os

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))


@shared_task
def createDomainRecord(createDomainResult, cfg):
    if not createDomainResult.get('success'):
        return {'error': 'Parent failed'}
    if 'user' not in cfg:
        return {'error': 'Missing user'}
    if 'domain' not in cfg:
        return {'error': 'Missing domain'}
    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        return {'error': 'Invalid username'}
    try:
        app_type = DockerContainer.objects.get(container_id=(cfg.get('app_type', 'zaro/php7')))
    except ObjectDoesNotExist:
        return {'error': 'Invalid app_type'}
    dbentry, created = DomainModel.objects.get_or_create(
        user=user,
        domain_name=cfg['domain'],
    )
    dbentry.app_type = app_type
    dbentry.save()
    return {'success': True}


@shared_task
def removeDomainRecord(createDomainResult, cfg):
    if not createDomainResult.get('success'):
        return {'error': 'Parent failed'}
    if 'user' not in cfg:
        return {'error': 'Missing user'}
    if 'domain' not in cfg:
        return {'error': 'Missing domain'}
    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        return {'error': 'Invalid username'}
    dbentry = DomainModel.objects.get(
        user=user,
        domain_name=cfg['domain'],
    )
    dbentry.delete()
    return {'success': True}


@shared_task
def addMysqlDatabaseRecord(createDomainResult, cfg):
    if not createDomainResult.get('success'):
        return {'error': 'Parent failed'}

    if not cfg.get('db_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('db_pass'):
        return {'error': 'Missing MySQL password'}
    if not cfg.get('db_name'):
        return {'error': 'Missing MySQL database name'}

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        return {'error': 'Invalid username'}
    dbentry, created = SharedDatabase.objects.get_or_create(
        user=user,
        db_user=cfg['db_user'],
        db_pass=cfg['db_pass'],
        db_name=cfg['db_name'],
        db_type="mysql"
    )
    dbentry.save()
    return {'success': True}


@shared_task
def removeMysqlDatabaseRecord(createDomainResult, cfg):
    if not createDomainResult.get('success'):
        return {'error': 'Parent failed'}

    if not cfg.get('db_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('db_name'):
        return {'error': 'Missing MySQL database name'}

    try:
        user = User.objects.get(username=cfg['user'])
        print(user)
    except ObjectDoesNotExist:
        return {'error': 'Invalid username'}

    dbentry = None
    # Permission check,  don't allow deleteuser/database if they are already taken by another user
    for dbentry in SharedDatabase.objects.filter(db_name=cfg['db_name'], db_user=cfg['db_user'], db_type="mysql"):
        if dbentry.user.username != cfg['user']:
            return {'error': "'{}'' is not owner of Database '{}' already exists!".format(cfg['user'], cfg['db_name']) }
        break

    if not dbentry:
        return {'error': "No such user/database '{}'/'{}' !".format(cfg['user'], cfg['db_name']) }

    dbentry.delete()
    return {'success': True}
