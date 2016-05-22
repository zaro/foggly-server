from celery.task import task
from .task_utils import *
from .dockerctl import DockerCtl

import logging

import MySQLdb


@task(name='host.createDomain')
def createDomain(cfg):
    try:
        user = cfg['user']
    except:
        return {'error': 'Missing user'}
    try:
        domain = cfg['domain']
    except:
        return {'error': 'Missing domain'}
    try:
        app_type = cfg['app_type']
    except:
        return {'error': 'Missing app_type'}
    try:
        ports = cfg['ports']
    except:
        return {'error': 'Missing ports'}

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
    hostCfg.set('OWNER', user)
    hostCfg.set('USE_CONTAINER', app_type['container_id'])
    hostCfg.set('PROXY_TYPE', app_type['proxy_type'])
    hostCfg.set('DOMAIN', domain)
    hostCfg.set('VHOST_DOMAIN', domain)
    hostCfg.set('DOMAIN_ID', domain.translate(str.maketrans(".-", "__")))
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

    td = TemplateDir(os.path.join(THIS_FILE_DIR, '../etc_template/'), hostCfg.asDict())
    td.copyTo(d.path)

    return {'success': True}


@task(name='host.removeDomain')
def removeDomain(cfg):
    try:
        user = cfg['user']
    except:
        return {'error': 'Missing user'}
    try:
        domain = cfg['domain']
    except:
        return {'error': 'Missing domain'}

    d = getDomainDir(user, domain)
    if d.exists():
        d.rmtree()

    return {'success': True}


@task(name='host.startDomain')
def startDomain(cfg):
    d = getDomainDir(cfg['user'], cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    if not d.exists() or not hostCfg.exists():
        return {'error': 'Invalid user/domain', 'r': cfg}
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
            return {'error': 'Cannot start {} container'.format(status) }
    dctl.runContainer(cfg['user'], cfg['domain'], hostCfg.get('USE_CONTAINER'))
    # open ssh port
    d.run('firewall-cmd --zone=public --add-port={}/tcp'.format(hostCfg.get('SSH_PORT')))
    # reload nginx config
    d.pushd('etc')
    if d.exists('site.conf.disabled'):
        d.mv('site.conf.disabled', 'site.conf')
    d.run('systemctl reload nginx')
    return {'success': True}


@task(name='host.stopDomain')
def stopDomain(cfg):
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


@task(name='host.addMysqlDatabase')
def addMysqlDatabase(cfg):
    logging.info('addMysqlDatabase({})'.format(cfg))
    if not cfg.get('db_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('db_pass'):
        return {'error': 'Missing MySQL password'}
    if not cfg.get('db_name'):
        return {'error': 'Missing MySQL database name'}

    queryList = [ s.format(**cfg) for s in [
        "CREATE DATABASE IF NOT EXISTS `{db_name}`;",
        "GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost' IDENTIFIED BY '{db_pass}';"
    ]]
    db = MySQLdb.connect(user="root")
    cur = db.cursor()
    res = []
    for q in queryList:
        print("EXEC:", q)
        cur.execute(q)
        res += cur.fetchall()
    return {'success': True, 'result': res }


@task(name='host.removeMysqlDatabase')
def removeMysqlDatabase(cfg):
    logging.info('removeMysqlDatabase({})'.format(cfg))

    if not cfg.get('db_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('db_name'):
        return {'error': 'Missing MySQL database name'}

    queryList = [ s.format(**cfg) for s in [
        "DROP DATABASE IF EXISTS `{db_name}`;",
        "REVOKE ALL PRIVILEGES ON `{db_name}`.* FROM '{db_user}'@'localhost';"
    ]]
    db = MySQLdb.connect(user="root")
    cur = db.cursor()
    res = []
    for q in queryList:
        print("EXEC:", q)
        cur.execute(q)
        res += cur.fetchall()
    return {'success': True, 'result': res }


@task(name='host.addPublicKey')
def addPublicKey(cfg):
    d = getDomainDir(cfg['user'], cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.addKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}


@task(name='host.removePublicKey')
def removePublicKey(cfg):
    d = getDomainDir(cfg['user'], cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.removeKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}
