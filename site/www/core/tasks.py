from celery import shared_task
from core.models import SharedDatabase, DomainModel, DomainConfig, DockerContainer, Host
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging


log = logging.getLogger('tasks')


class HostControllerError(Exception):
    pass


def mandatoryParams(cfg, *params):
    out = {}
    for param in params:
        if cfg.get(param) is None:
            raise HostControllerError("Missing parameter '{}'".format(param))
        out[param] = cfg.get(param)
    return out


@shared_task
def createDomainRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'domain', 'app_type')
    if 'domainConfig' not in createDomainResult:
        raise HostControllerError('Create domain  failed to provide "domainConfig"')

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username')
    try:
        app_type = DockerContainer.objects.get(container_id=cfg['app_type']['container_id'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid application type')
    try:
        host = Host.objects.get(main_domain=cfg['host'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid host')

    dbentry, created = DomainModel.objects.get_or_create(
        user=user,
        domain_name=cfg['domain'],
        host=host
    )
    dbentry.app_type = app_type
    dbentry.save()
    dConf = createDomainResult['domainConfig']
    dbentry.domainconfig_set.set(
        [DomainConfig(key=k, value=v) for k, v in dConf.items()],
        bulk=False, clear=True
    )
    return {'success': True}


@shared_task
def removeDomainRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'domain')

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username')
    dbentry = DomainModel.objects.get(
        user=user,
        domain_name=cfg['domain'],
    )
    dbentry.delete()
    return {'success': True}


@shared_task
def addMysqlDatabaseRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'db_user', 'db_pass', 'db_name', 'host')

    log.info('addMysqlDatabaseRecord({}, {})'.format(createDomainResult, cfg))
    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username')
    try:
        host = Host.objects.get(main_domain=cfg['host'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid host')

    dbentry, created = SharedDatabase.objects.get_or_create(
        user=user,
        host=host,
        db_user=cfg['db_user'],
        db_pass=cfg['db_pass'],
        db_name=cfg['db_name'],
        db_type="mysql"
    )
    dbentry.save()
    return {'success': True}


@shared_task
def removeMysqlDatabaseRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'db_user', 'db_name', 'host')

    try:
        user = User.objects.get(username=cfg['user'])
        print(user)
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username')

    dbentry = None
    # Permission check,  don't allow deleteuser/database if they are already taken by another user
    for dbentry in SharedDatabase.objects.filter(db_name=cfg['db_name'], db_user=cfg['db_user'], db_type='mysql', host=cfg['host']):
        if dbentry.user.username != cfg['user']:
            raise HostControllerError("'{}'' is not owner of database '{}'!".format(cfg['user'], cfg['db_name']))
        break

    if not dbentry:
        raise HostControllerError("No such user/database '{}'/'{}' !".format(cfg['user'], cfg['db_name']))

    dbentry.delete()
    return {'success': True}
