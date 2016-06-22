from celery import shared_task
from .task_utils import *
from .dockerctl import DockerCtl

from django.conf import settings
import logging
import json
import redis
import os
import MySQLdb

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('tasks')


class HostWorkerError(Exception):
    pass


def mandatoryParams(cfg, *params):
    out = {}
    for param in params:
        if cfg.get(param) is None:
            raise HostWorkerError("Missing parameter '{}'".format(param))
        out[param] = cfg.get(param)
    return out


@shared_task(name='host.getDomainConfig')
def getDomainConfig(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(user, domain)
    if d.existing():
        return {'success': True, 'domainConfig': d.asDict()}
    raise HostWorkerError('Invalid user/domain')


@shared_task(name='host.createDomain')
def createDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain', 'app_type')
    ports = cfg.get('ports') or {}
    user = cfg['user']
    domain = cfg['domain']
    app_type = cfg['app_type']

    # hardcode www-data user for now
    nginxUID = 33
    nginxGID = 33

    d = getDomainDir(user, domain)
    d.mkdir(uid=nginxUID, gid=nginxGID)
    d.mkdir('tmp', mode=0o777)
    d.mkdir('tmp/rsyslog')

    d.mkdir('var/run')
    d.mkdir('var/lock')
    d.mkdir('var/spool/postfix')
    d.mkdir('var/spool/rsyslog')
    d.mkdir('var/spool/sessions', nginxUID, mode=0o1733)

    d.pushd('www')
    d.mkdir([], nginxUID, nginxGID)
    if not d.exists('.git'):
        d.run("git init .")
    d.run("git config receive.denyCurrentBranch updateInstead")
    with open(d.filename('.git/hooks/post-receive'), 'w') as f:
        f.write('#!/bin/bash\n\n[ -x /usr/local/deploy_hook ] && exec /usr/local/deploy_hook\n')
    d.chmod(0o755, '.git/hooks/post-receive')
    d.run("chown -R {}:{} .git".format(nginxUID, nginxGID))
    d.popd()

    d.mkdir('run', nginxUID, nginxGID)
    d.mkdir(['log/nginx', 'log/apache2'], nginxUID, nginxGID)
    d.mkdir(['log/supervisor'])

    d.pushd('.ssh')
    d.mkdir([], nginxUID, nginxGID, 0o700)
    if not d.exists('id_rsa', 'id_rsa.pub'):
        d.rm('id_rsa', 'id_rsa.pub')
        d.run("ssh-keygen -q -f id_rsa -N '' -t rsa -C '{domain}'".format(domain=cfg['domain']))
    d.popd()

    hostCfg = DomainConfig(d.filename('.hostcfg'), d.clone().filename('*/*/.hostcfg'))
    hostCfg.override(True)
    hostCfg.set('OWNER', user)
    hostCfg.set('DOMAIN', domain)
    hostCfg.set('VHOST_DOMAIN', domain)
    hostCfg.set('DOMAIN_ID', domain.translate(str.maketrans(".-", "__")))
    hostCfg.set('USE_CONTAINER', app_type['container_id'])
    hostCfg.set('PROXY_TYPE', app_type['proxy_type'])
    hostCfg.override(False)

    if 'ssh' in ports:
        hostCfg.set('SSH_PORT', ports['ssh'])
    else:
        hostCfg.genUniqInt('SSH_PORT', 12300, 12399)
    if 'www' in ports:
        hostCfg.set('WWW_PORT', ports['www'])
    else:
        hostCfg.genUniqInt('WWW_PORT', 8800, 8899)

    hostCfg.write()

    d.pushd('etc')
    d.pushd('ssh')
    d.mkdir()
    for algo in ['rsa', 'dsa', 'ecdsa', 'ed25519']:
        hKey = 'ssh_host_{algo}_key'.format(algo=algo)
        if not d.exists(hKey, hKey + '.pub'):
            d.rm(hKey, hKey + '.pub')
            d.run("ssh-keygen -q -f {hKey} -N '' -t {algo} ".format(algo=algo, hKey=hKey))
    d.popd()

    td = TemplateDir(os.path.join(THIS_FILE_DIR, '../../etc_template/'), hostCfg.asDict())
    td.copyTo(d.path)

    return {'success': True, 'domainConfig': hostCfg.asDict()}


@shared_task(name='host.removeDomain')
def removeDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    if not d.exists():
        raise HostWorkerError('Invalid user/domain')

    dctl = DockerCtl(baseUrl='unix://')
    status = dctl.getContainerStatus(cfg['user'], cfg['domain'])
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'exited':
            dctl.rmContainer(cfg['user'], cfg['domain'])

    d.rmtree()

    return {'success': True}


@shared_task(name='host.startDomain')
def startDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    if not d.exists() or not hostCfg.exists():
        raise HostWorkerError('Invalid user/domain')
    # start container
    dctl = DockerCtl(baseUrl='unix://')
    status = dctl.getContainerStatus(cfg['user'], cfg['domain'])
    print('Current status :', status)
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'exited':
            dctl.rmContainer(cfg['user'], cfg['domain'])
        else:
            raise HostWorkerError('Cannot start {} container'.format(status))
    dctl.runContainer(cfg['user'], cfg['domain'], hostCfg.get('USE_CONTAINER'))
    # open ssh port
    d.run('firewall-cmd --zone=public --add-port={}/tcp'.format(hostCfg.get('SSH_PORT')))
    # reload nginx config
    d.pushd('etc')
    if d.exists('site.conf.disabled'):
        d.mv('site.conf.disabled', 'site.conf')
    d.run('systemctl reload nginx')
    return {'success': True}


@shared_task(name='host.stopDomain')
def stopDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    dctl = DockerCtl(baseUrl='unix://')
    status = dctl.getContainerStatus(cfg['user'], cfg['domain'])
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'exited':
            dctl.rmContainer(cfg['user'], cfg['domain'])
    # close ssh port
    d.run('firewall-cmd --zone=public --remove-port={}/tcp'.format(hostCfg.get('SSH_PORT')))
    # reload nginx config
    d.pushd('etc')
    if d.exists('site.conf'):
        d.mv('site.conf', 'site.conf.disabled')
    d.run('systemctl reload nginx')
    return {'success': True}


def prepareQueryList(cfg, qList):
    queryList = []
    for o in qList:
        if type(o) is str:
            queryList.append({
                'q': o.format(**cfg),
                'ignoreErrors': []
            })
        elif type(o) in [tuple, list]:
            s, *ignoreErrors = o
            queryList.append({
                'q': s.format(**cfg),
                'ignoreErrors': ignoreErrors
            })
        elif type(o) is dict:
            queryList.append({
                'q': o.q.format(**cfg),
                'ignoreErrors': o.ignoreErrors
            })
    return queryList


def executeQueryList(queryList):
    db = MySQLdb.connect(user="root")
    cur = db.cursor()
    res = []
    for query in queryList:
        print("EXEC:", query['q'])
        try:
            cur.execute(query['q'])
        except MySQLdb.OperationalError as e:
            if e.args[0] not in query['ignoreErrors']:
                raise e
        res += cur.fetchall()
    return res


@shared_task(name='host.addMysqlDatabase')
def addMysqlDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_pass', 'db_name')
    logger.info('addMysqlDatabase({})'.format(cfg))

    queryList = prepareQueryList(cfg, [
        "CREATE DATABASE IF NOT EXISTS `{db_name}`;",
        "GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost' IDENTIFIED BY '{db_pass}';"
    ])
    res = executeQueryList(queryList)
    return {'success': True, 'result': res }


@shared_task(name='host.removeMysqlDatabase')
def removeMysqlDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_name')
    logger.info('removeMysqlDatabase({})'.format(cfg))

    queryList = prepareQueryList(cfg, [
        "DROP DATABASE IF EXISTS `{db_name}`;",
        ("REVOKE ALL PRIVILEGES ON `{db_name}`.* FROM '{db_user}'@'localhost';", 1141)
    ])
    res = executeQueryList(queryList)
    return {'success': True, 'result': res }


@shared_task(name='host.addPublicKey')
def addPublicKey(cfg):
    mandatoryParams(cfg, 'user', 'domain', 'publicKey')

    d = getDomainDir(cfg['user'], cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.addKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}


@shared_task(name='host.removePublicKey')
def removePublicKey(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.removeKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}

redisPool = None
currentHostName = None


def getCurrentHostname():
    global currentHostName
    if currentHostName is not None:
        return currentHostName
    if 'HOST_WORKER_QUEUE' in os.environ:
        currentHostName = os.environ['HOST_WORKER_QUEUE']
        return currentHostName
    import platform
    currentHostName = platform.node()
    return currentHostName


def getRedisConnection():
    global redisPool
    if redisPool is None:
        redisPool = redis.ConnectionPool.from_url(settings.CELERY_RESULT_BACKEND)
    return redis.StrictRedis(connection_pool=redisPool)


@shared_task(name='host.dockerStatus')
def dockerStatus(prevResult, cfg):
    containersList = DockerCtl('unix://').listContainers()
    containers = {}
    statusMap = {'exited': 'down', 'removal': 'down', 'dead': 'down'}
    for cont in containersList:
        domain = cont['Names'][0][1:]
        containers[domain] = {
            'domain': domain,
            'type': cont['Image'],
            'status': cont['Status'],
            'created': cont['Created'],
            'state': statusMap[cont['state']] if cont['state'] in statusMap else cont['state'],
        }
    r = getRedisConnection()
    key = 'dockerStatus:' + getCurrentHostname()
    expiry = int(cfg.get("update_interval", 10)) + 1
    r.set(key, json.dumps(containers), ex=expiry)