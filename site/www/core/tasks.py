from celery import shared_task
from core.models import SharedDatabase, DomainModel, DomainConfig, ContainerRuntime, Host
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging
from host_worker.tasks import certbotRenew

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
def certbotRenewAllHosts():
    # TODO: Rework to use broadcast queue
    for host in Host.objects.all():
        certbotRenew.s().set(queue=host.main_domain).apply_async()


@shared_task
def createDomainRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'domain', 'app_type', 'host')
    if 'domainConfig' not in createDomainResult:
        raise HostControllerError('Create domain  failed to provide "domainConfig"')

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username: {}'.format(cfg['user']))
    try:
        app_type = ContainerRuntime.objects.get(id=cfg['app_type']['id'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid application type id: {}'.format(cfg['app_type']['id']))
    try:
        host = Host.objects.get(main_domain=cfg['host'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid host: {}', cfg['host'])

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
def updateDomainConfig(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'domain', 'host')
    if 'domainConfig' not in createDomainResult:
        raise HostControllerError('Create domain  failed to provide "domainConfig"')

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username: {}'.format(cfg['user']))
    try:
        host = Host.objects.get(main_domain=cfg['host'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid host: {}', cfg['host'])

    dbentry, created = DomainModel.objects.get_or_create(
        user=user,
        domain_name=cfg['domain'],
        host=host
    )
    dConf = createDomainResult['domainConfig']
    for k, v in dConf.items():
        DomainConfig.objects.update_or_create(key=k, domain=dbentry, defaults={'value': v})
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
def addDatabaseRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'db_user', 'db_pass', 'db_name', 'host', 'db_type')

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
        db_type=cfg['db_type']
    )
    dbentry.save()
    return {'success': True}


@shared_task
def removeDatabaseRecord(createDomainResult, cfg):
    mandatoryParams(cfg, 'user', 'db_user', 'db_name', 'host', 'db_type')

    try:
        user = User.objects.get(username=cfg['user'])
        print(user)
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid username')
    try:
        host = Host.objects.get(main_domain=cfg['host'])
    except ObjectDoesNotExist:
        raise HostControllerError('Invalid host')

    dbentry = None
    # Permission check,  don't allow deleteuser/database if they are already taken by another user
    for dbentry in SharedDatabase.objects.filter(db_name=cfg['db_name'], db_user=cfg['db_user'], db_type=cfg['db_type'], host=host):
        if dbentry.user.username != cfg['user']:
            raise HostControllerError("'{}'' is not owner of database '{}'!".format(cfg['user'], cfg['db_name']))
        break

    if not dbentry:
        raise HostControllerError("No such user/database '{}'/'{}' !".format(cfg['user'], cfg['db_name']))

    dbentry.delete()
    return {'success': True}
