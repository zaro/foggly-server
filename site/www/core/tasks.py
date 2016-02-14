from celery import shared_task
from core.task_utils import *
from core.dockerctl import DockerCtl
from django.db.models import Q
from core.models import SharedDatabase, DomainModel, DockerContainer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import logging
import os
from pwd import getpwnam
from grp import getgrnam

import MySQLdb

THIS_FILE_DIR=os.path.dirname(os.path.abspath(__file__))

@shared_task
def createDomain(cfg):
    if 'user' not in cfg:
        return {'error': 'Missing user'}
    if 'domain' not in cfg:
        return {'error': 'Missing domain'}

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        return {'error':'Invalid username'}

    try:
        app_type = DockerContainer.objects.get(container_id=(cfg.get('app_type', 'zaro/php7')))
    except ObjectDoesNotExist:
        return {'error':'Invalid app_type'}

    # Permission check,  don't allow adding user/database if they are already taken by another user
    for dbentry in DomainModel.objects.filter(domain_name=cfg['domain']):
        if dbentry.user.username != cfg['user']:
            return {'error': "Domain '{}' already exists!".format(cfg['domain']) }

    # hardcode www-data user for now
    nginxUID = 33
    nginxGID = 33

    d = getDomainDir(cfg['user'] ,  cfg['domain'])
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
    d.chmod(0o755,'.git/hooks/post-receive')
    d.run("chown -R {}:{} .git".format(nginxUID, nginxGID))
    d.popd()

    d.mkdir('run', nginxUID, nginxGID)
    d.mkdir(['log/nginx', 'log/apache2'], nginxUID, nginxGID)
    d.mkdir(['log/supervisor'])

    d.pushd('.ssh')
    d.mkdir([], nginxUID, nginxGID, 0o700)
    if not d.exists('id_rsa','id_rsa.pub'):
        d.rm('id_rsa', 'id_rsa.pub')
        d.run("ssh-keygen -q -f id_rsa -N '' -t rsa -C '{domain}'".format(domain=cfg['domain']))
    d.popd()

    hostCfg = DomainConfig(d.filename('.hostcfg'), d.clone().filename('*/*/.hostcfg'))
    hostCfg.set('OWNER', user.username)
    hostCfg.set('USE_CONTAINER', app_type.container_id)
    hostCfg.set('PROXY_TYPE', app_type.proxy_type)
    hostCfg.set('DOMAIN', cfg['domain'])
    hostCfg.set('DOMAIN_ID', cfg['domain'].translate(str.maketrans(".-","__")))
    hostCfg.genUniqInt('SSH_PORT', 12300, 12399)
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

    td = TemplateDir(os.path.join(THIS_FILE_DIR,'../../../etc_template/'), hostCfg.asDict())
    td.copyTo(d.path)

    dbentry, created = DomainModel.objects.get_or_create(
        user=user,
        domain_name=cfg['domain'],
        )
    dbentry.app_type = app_type
    dbentry.save()

    return {'success': True}

@shared_task
def startDomain(cfg):
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    if not d.exists() or not hostCfg.exists():
        return {'error': 'Invalid user/domain', 'r':cfg}
    # start container
    dctl = DockerCtl()
    status  = dctl.getContainerStatus(cfg['user'], cfg['domain'])
    print('Current status :', status)
    if status != None:
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

@shared_task
def stopDomain(cfg):
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    dctl = DockerCtl()
    status  = dctl.getContainerStatus(cfg['user'], cfg['domain'])
    if status != None:
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

@shared_task
def addMysqlDatabase(cfg):
    logging.info('addMysqlDatabase({})'.format(cfg))
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    if not cfg.get('mysql_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('mysql_password'):
        return {'error': 'Missing MySQL password'}
    if not cfg.get('mysql_db'):
        return {'error': 'Missing MySQL database name'}

    try:
        user = User.objects.get(username=cfg['user'])
    except ObjectDoesNotExist:
        return {'error':'Invalid username'}

    # Permission check,  don't allow adding user/database if they are already taken by another user
    for dbentry in SharedDatabase.objects.filter(Q(db_name=cfg['mysql_db']) | Q(db_user=cfg['mysql_user']), db_type="mysql"):
        if dbentry.user.username != cfg['user']:
            if dbentry.db_name == cfg['mysql_db']:
                return {'error': "Database '{}' already exists!".format(cfg['mysql_db']) }
            if dbentry.db_user == cfg['db_user']:
                return {'error': "Username '{}' already taken!".format(cfg['mysql_db']) }

    queryList = [ s.format(**cfg) for s in [
        "CREATE DATABASE IF NOT EXISTS `{mysql_db}`;",
        "GRANT ALL PRIVILEGES ON `{mysql_db}`.* TO '{mysql_user}'@'localhost' IDENTIFIED BY '{mysql_password}';"
    ]]
    db=MySQLdb.connect(user="root")
    cur = db.cursor()
    res = []
    for q in queryList:
        print("EXEC:", q)
        cur.execute(q)
        res += cur.fetchall()
    dbentry, created = SharedDatabase.objects.get_or_create(
        user=user,
        db_user=cfg['mysql_user'],
        db_pass=cfg['mysql_password'],
        db_name=cfg['mysql_db'],
        db_type="mysql"
        )
    dbentry.save()
    return {'success': True, 'result': res }

@shared_task
def removeMysqlDatabase(cfg):
    logging.info('addMysqlDatabase({})'.format(cfg))
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    if not cfg.get('mysql_user'):
        return {'error': 'Missing MySQL user'}
    if not cfg.get('mysql_db'):
        return {'error': 'Missing MySQL database name'}

    try:
        user = User.objects.get(username=cfg['user'])
        print(user)
    except ObjectDoesNotExist:
        return {'error':'Invalid username'}

    dbentry = None
    # Permission check,  don't allow deleteuser/database if they are already taken by another user
    for dbentry in  SharedDatabase.objects.filter(db_name=cfg['mysql_db'], db_user=cfg['mysql_user'], db_type="mysql"):
        if dbentry.user.username != cfg['user']:
            return {'error': "'{}'' is not owner of Database '{}' already exists!".format(cfg['user'], cfg['mysql_db']) }
        break

    if not dbentry:
        return {'error': "No such user/database '{}'/'{}' !".format(cfg['user'], cfg['mysql_db']) }

    queryList = [ s.format(**cfg) for s in [
        "DROP DATABASE IF EXISTS `{mysql_db}`;",
        "REVOKE ALL PRIVILEGES ON `{mysql_db}`.* FROM '{mysql_user}'@'localhost';"
    ]]
    db=MySQLdb.connect(user="root")
    cur = db.cursor()
    res = []
    for q in queryList:
        print("EXEC:", q)
        cur.execute(q)
        res += cur.fetchall()
    dbentry.delete()
    return {'success': True, 'result': res }

@shared_task
def addPublicKey(cfg):
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.addKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}

@shared_task
def removePublicKey(cfg):
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    kf = AuthorizedKeysFile(d)
    kf.removeKey(cfg['publicKey'])
    kf.writeFile()
    return {'success': True}
