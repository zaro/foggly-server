from celery import shared_task
from core.task_utils import *
from core.dockerctl import DockerCtl

import os
from pwd import getpwnam
from grp import getgrnam

THIS_FILE_DIR=os.path.dirname(os.path.abspath(__file__))

@shared_task
def createDomainDir(cfg):
    # hardcode www-data user for now
    nginxUID = 33
    nginxGID = 33

    if 'user' not in cfg:
        return {'error': 'Missing user'}
    if 'domain' not in cfg:
        return {'error': 'Missing domain'}
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    d.mkdir()
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
            f.write('!#/bin/bash\n\n[ -x /usr/local/deploy_hook ] && exec /usr/local/deploy_hook\n')
        d.chmod('.git/hooks/post-receive', 0o755)
        d.run("chown -R www-data.www-data .git")
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
    hostCfg.set('USE_CONTAINER', 'zaro/php7')
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
    return {'success': True}

@shared_task
def startDomain(cfg):
    d = getDomainDir(cfg['user'] ,  cfg['domain'])
    hostCfg = DomainConfig(d.filename('.hostcfg'))
    if not d.exists() or not hostCfg.exists():
        return {'error': 'Invalid user/domain'}
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
