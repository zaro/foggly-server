from celery import shared_task
from .task_utils import getDomainDir, TemplateDir, DomainConfig, LETSENCRYPT_DIR, DirCreate, AuthorizedKeysFile
from .dockerctl import DockerCtl
from .systemdctl import SystemdCtl
from .firewalldctl import FirewalldCtl

from django.conf import settings
import logging
import json
import redis
import os
import MySQLdb
import psycopg2
import socket
import uuid
from pwd import getpwnam

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('tasks')

KEY_DIR = '/srv/home/www/persistent/opendkim/keys/'


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

    d = getDomainDir(cfg['user'], cfg['domain'])
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

    wwwDataPwdEntry = getpwnam('www-data')
    nginxUID = wwwDataPwdEntry.pw_uid
    nginxGID = wwwDataPwdEntry.pw_gid

    postfixPwdEntry = getpwnam('postfix')
    postfixUID = postfixPwdEntry.pw_uid
    postfixGID = postfixPwdEntry.pw_gid

    d = getDomainDir(user, domain)
    d.mkdir(uid=nginxUID, gid=nginxGID)
    d.mkdir('tmp', mode=0o777)

    if not d.exists('.bashrc'):
        with open(d.filename('.bashrc'), 'w') as f:
            f.write('[ -f ~/pyvenv/bin/activate ] && . ~/pyvenv/bin/activate\n')
            f.write('export PATH=$PATH:~/www/node_modules/.bin/\n')

    if not d.exists('.bash_profile'):
        with open(d.filename('.bash_profile'), 'w') as f:
            f.write('[[ -r ~/.bashrc ]] && . ~/.bashrc\n')

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

    d.mkdir(['log', 'log/nginx', 'log/journal'], nginxUID, nginxGID)

    d.pushd('.ssh')
    d.mkdir([], nginxUID, nginxGID, 0o700)
    if not d.exists('id_rsa', 'id_rsa.pub'):
        d.rm('id_rsa', 'id_rsa.pub')
        d.run("ssh-keygen -q -f id_rsa -N '' -t rsa -C '{domain}'".format(domain=cfg['domain']))
    d.popd()

    masterDomain = socket.getfqdn()
    hostCfg = DomainConfig(d.filename('.hostcfg'), d.clone(True).filename('*/*/.hostcfg'))
    # Generate container UUID accorging to https://www.freedesktop.org/wiki/Software/systemd/ContainerInterface/
    hostCfg.set('container_uuid', str(uuid.uuid4()))
    hostCfg.override(True)
    hostCfg.set('OWNER', user)
    hostCfg.set('MASTER_DOMAIN', masterDomain)
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

    # Ssh Keys generation
    d.pushd('etc')
    d.pushd('ssh')
    d.mkdir()
    for algo in ['rsa', 'dsa', 'ecdsa', 'ed25519']:
        hKey = 'ssh_host_{algo}_key'.format(algo=algo)
        if not d.exists(hKey, hKey + '.pub'):
            d.rm(hKey, hKey + '.pub')
            d.run("ssh-keygen -q -f {hKey} -N '' -t {algo} ".format(algo=algo, hKey=hKey))
    d.popd()

    # opendkim Keys generation
    d.pushd('opendkim')
    d.pushd('keys')
    d.mkdir(uid=postfixUID, gid=postfixGID)
    dkimPriv = '{domain}.private'.format(domain=domain)
    dkimTxt = '{domain}.txt'.format(domain=domain)
    if not d.exists(dkimPriv, dkimTxt):
        d.run("opendkim-genkey -s fogglymail -d {domain} ".format(domain=domain))
        d.mv('fogglymail.private', dkimPriv)
        d.mv('fogglymail.txt', dkimTxt)
    d.chown(postfixUID, postfixGID, dkimPriv)
    d.chmod(0o644, dkimTxt)
    d.cpIfExist(KEY_DIR + '{domain}.private'.format(domain=masterDomain))
    d.popd()
    d.popd()

    td = TemplateDir(os.path.join(THIS_FILE_DIR, '../etc_template/'), hostCfg.asDict())
    td.copyTo(d.path)

    # TODO:
    # chmod 644 /srv/home/etc/postfix/*.cf /srv/home/etc/postfix/postfix-files
    # chmod 644 /srv/home/etc/postfix/virtual
    # chmod 755 /srv/home/etc/postfix/post-install /srv/home/etc/postfix/postfix-script

    return {'success': True, 'domainConfig': hostCfg.asDict()}


@shared_task(name='host.enableDomainSsl')
def enableDomainSsl(cfg):
    mandatoryParams(cfg, 'user', 'domain')
    sslOnly = str(cfg.get('sslOnly', 'no')).lower()

    if sslOnly != 'yes':
        sslOnly = 'no'

    d = getDomainDir(cfg['user'], cfg['domain'])
    if not d.exists():
        raise HostWorkerError('Invalid user/domain')

    d.mkdir('.well-known')

    d.run("certbot certonly --agree-tos --non-interactive --config-dir {cfgdir} --webroot -w {webroot} -d {domain}".format(
        webroot=d.filename('.well-known'),
        domain=cfg['domain'],
        cfgdir=LETSENCRYPT_DIR,
    ))

    hostCfg = DomainConfig(d.filename('.hostcfg'))
    hostCfg.override(True)
    hostCfg.set('HAS_SSL', 'yes')
    hostCfg.set('SSL_ONLY', sslOnly)
    hostCfg.override(False)

    hostCfg.write()

    td = TemplateDir(os.path.join(THIS_FILE_DIR, '../etc_template/'), hostCfg.asDict())
    td.copyFileTo('site.conf', d.filename('etc'))

    SystemdCtl().reloadUnit('nginx.service')

    return {'success': True, 'domainConfig': {'HAS_SSL': 'yes'}}


@shared_task(name='host.certbotRenew')
def certbotRenew():
    try:
        DirCreate('/tmp').run("certbot --agree-tos --non-interactive --config-dir {cfgdir} renew".format(
            cfgdir=LETSENCRYPT_DIR,
        ))
    except:
        # this will fail even if only one domain fails
        # so ignore it
        pass

    SystemdCtl().reloadUnit('nginx.service')

    return {'success': True}


@shared_task(name='host.removeDomain')
def removeDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    if not d.exists():
        raise HostWorkerError('Invalid user/domain')

    dctl = DockerCtl()
    status = dctl.getContainerState(cfg['user'], cfg['domain'])
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'down':
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
    dctl = DockerCtl()
    status = dctl.getContainerState(cfg['user'], cfg['domain'])
    print('Current status :', status)
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'down':
            dctl.rmContainer(cfg['user'], cfg['domain'])
        else:
            raise HostWorkerError('Cannot start {} container'.format(status))
    dctl.runContainer(cfg['user'], cfg['domain'], hostCfg.get('USE_CONTAINER'))
    # write domain state
    d.writeFile('.domainstate', 'started')
    # open ssh port
    # d.run('firewall-cmd --zone=public --add-port={}/tcp'.format(hostCfg.get('SSH_PORT')))
    FirewalldCtl().addPort(hostCfg.get('SSH_PORT'))
    # reload nginx config
    d.pushd('etc')
    d.ln_sf('site.conf', 'site.conf.enabled')
    # d.run('systemctl reload nginx')
    SystemdCtl().reloadUnit('nginx.service')
    return {'success': True}


@shared_task(name='host.stopDomain')
def stopDomain(cfg):
    mandatoryParams(cfg, 'user', 'domain')

    d = getDomainDir(cfg['user'], cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    if not d.exists() or not hostCfg.exists():
        raise HostWorkerError('Invalid user/domain')
    dctl = DockerCtl()
    status = dctl.getContainerState(cfg['user'], cfg['domain'])
    if status is not None:
        # stop/rm container
        if status == 'up':
            dctl.stopContainer(cfg['user'], cfg['domain'])
            dctl.rmContainer(cfg['user'], cfg['domain'])
        elif status == 'down':
            dctl.rmContainer(cfg['user'], cfg['domain'])
    # write domain state
    d.writeFile('.domainstate', 'stopped')
    # close ssh port
    # d.run('firewall-cmd --zone=public --remove-port={}/tcp'.format(hostCfg.get('SSH_PORT')))
    FirewalldCtl().removePort(hostCfg.get('SSH_PORT'))
    # reload nginx config
    d.pushd('etc')
    d.rm('site.conf.enabled')
    # d.run('systemctl reload nginx')
    SystemdCtl().reloadUnit('nginx.service')
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


def executeMysqlQueryList(queryList):
    db = MySQLdb.connect(user="root", unix_socket="/var/run/mysqld/mysqld.sock")
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


@shared_task(name='host.addDatabase')
def addDatabase(cfg):
    mandatoryParams(cfg, 'db_type')
    if cfg['db_type'] == 'mysql':
        return addMysqlDatabase(cfg)
    elif cfg['db_type'] == 'postgres':
        return addPostgresDatabase(cfg)
    raise HostWorkerError("Invalid database type: {}".format(cfg['db_type']))


@shared_task(name='host.removeDatabase')
def removeDatabase(cfg):
    mandatoryParams(cfg, 'db_type')
    if cfg['db_type'] == 'mysql':
        return removeMysqlDatabase(cfg)
    elif cfg['db_type'] == 'postgres':
        return removePostgresDatabase(cfg)
    raise HostWorkerError("Invalid database type: {}".format(cfg['db_type']))


@shared_task(name='host.addMysqlDatabase')
def addMysqlDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_pass', 'db_name')
    logger.info('addMysqlDatabase({})'.format(cfg))

    queryList = prepareQueryList(cfg, [
        "CREATE DATABASE IF NOT EXISTS `{db_name}`;",
        "GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost' IDENTIFIED BY '{db_pass}';"
    ])
    res = executeMysqlQueryList(queryList)
    return {'success': True, 'result': res}


@shared_task(name='host.removeMysqlDatabase')
def removeMysqlDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_name')
    logger.info('removeMysqlDatabase({})'.format(cfg))

    queryList = prepareQueryList(cfg, [
        "DROP DATABASE IF EXISTS `{db_name}`;",
        ("REVOKE ALL PRIVILEGES ON `{db_name}`.* FROM '{db_user}'@'localhost';", 1141)
    ])
    res = executeMysqlQueryList(queryList)
    return {'success': True, 'result': res}


def executePgQueryList(queryList, dbname='template1'):
    db = psycopg2.connect("dbname={dbname} user={user} password={password}".format(
        dbname=dbname,
        user=settings.HOST_WORKER_PG_USER,
        password=settings.HOST_WORKER_PG_PASS,
    ))
    db.autocommit = True
    cur = db.cursor()
    res = []
    for query in queryList:
        print("EXEC:", query['q'])
        try:
            cur.execute(query['q'])
        except psycopg2.Error as e:
            if e.pgcode not in query['ignoreErrors']:
                raise e
        if cur.rowcount and cur.rowcount > 0:
            res += cur.fetchall()
    return res


@shared_task(name='host.addPostgresDatabase')
def addPostgresDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_pass', 'db_name', 'db_type')
    logger.info('addPostgresDatabase({})'.format(cfg))

    # Taken from https://wiki.postgresql.org/wiki/Shared_Database_Hosting
    queryList = prepareQueryList(cfg, [
        # ('CREATE ROLE "{db_name}" NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOLOGIN', '42710'),
        ("CREATE ROLE \"{db_user}\" WITH NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN ENCRYPTED PASSWORD '{db_pass}'", '42710'),
        # 'GRANT "{db_name}" TO "{db_user}"',
        ('CREATE DATABASE "{db_name}" WITH OWNER="{db_user}"', '42P04'),
        'REVOKE ALL ON DATABASE "{db_name}" FROM public',
    ])
    res = executePgQueryList(queryList)

    return {'success': True, 'result': res}


@shared_task(name='host.removePostgresDatabase')
def removePostgresDatabase(cfg):
    mandatoryParams(cfg, 'db_user', 'db_name', 'db_type')
    logger.info('removePostgresDatabase({})'.format(cfg))

    queryList = prepareQueryList(cfg, [
        ('DROP DATABASE "{db_name}"', '3D000'),
        ('DROP ROLE "{db_user}"', '42704'),
        # ('DROP ROLE "{db_name}"', '42704'),
    ])
    res = executePgQueryList(queryList)
    return {'success': True, 'result': res}


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
        redisPool = redis.ConnectionPool.from_url(settings.REDIS_URL)
    return redis.StrictRedis(connection_pool=redisPool)


def getDockerStatus():
    containersList = DockerCtl().listContainers()
    containers = {}
    for cont in containersList:
        containers[cont['domain']] = cont
    return containers


@shared_task(name='host.dockerStatus')
def dockerStatus(prevResult, cfg):
    containers = getDockerStatus()
    r = getRedisConnection()
    key = 'dockerStatus:' + getCurrentHostname()
    expiry = int(cfg.get("update_interval", 10)) + 1
    r.set(key, json.dumps(containers), ex=expiry)
