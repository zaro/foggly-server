from celery import shared_task

import os, subprocess
from pwd import getpwnam
from grp import getgrnam

class DirCreate:
    def __init__(self, path):
        self.paths = [ path ]
        self.path = path

    def pushd(self, path):
        if path :
            self.paths.append(path)
            self.path = os.path.join( *self.paths )
            self.path = os.path.abspath(self.path)
        print("pushd :" , self.path)

    def popd(self):
        self.paths.pop()
        self.path = os.path.join( *self.paths )
        self.path = os.path.abspath(self.path)
        print("popd " , self.path)

    def _mkdir(self, uid=-1, gid=-1, mode=None):
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass
        if uid >= 0 or gid >= 0:
            os.chown(self.path, uid, gid)
        if mode:
            os.chmod(self.path, mode)

    def mkdir(self, paths=None, uid=-1, gid=-1, mode=None):
        if not paths or len(paths)==0:
            return self._mkdir(uid, gid, mode)

        if type(paths) != list:
            paths = [ paths ]
        for path in paths:
            self.pushd(path)
            self._mkdir(uid, gid, mode)
            self.popd()
    def exists(self, path):
        return os.path.exists( os.path.join( self.path, path ) )
    def run(self, cmd, *args):
        subprocess.run(cmd, shell=True, check=True, cwd=self.path, *args)

@shared_task
def createDomainDir(cfg):
    #nginxUID = getpwnam('nginx')[2]
    #nginxGID = getgrnam('nginx')[2]
    nginxUID = 501
    nginxGID = 20
    d = DirCreate('/tmp/srv/')
    if 'user' not in cfg:
        return {'error': 'Missing user'}
    d.pushd( cfg['user'] )
    if 'domain' not in cfg:
        return {'error': 'Missing domain'}
    d.pushd( cfg['domain'] )
    d.mkdir()
    d.mkdir('tmp', mode=0o777)
    d.mkdir('tmp/rsyslog')

    d.mkdir('spool/postfix')
    d.mkdir('spool/sessions', nginxUID, mode=0o1733)

    d.pushd('www')
    d.mkdir([], nginxUID, nginxGID)
    if not d.exists('.git'):
        d.run("git init .")
        d.run("git config receive.denyCurrentBranch updateInstead")
    d.popd()

    d.mkdir('run', nginxUID, nginxGID)
    d.mkdir(['log', 'log/nginx'], nginxUID, nginxGID)

    d.pushd('.ssh')
    d.mkdir([], nginxUID, nginxGID, 0o700)
    d.run("ssh-keygen -q -f id_rsa -N '' -t rsa -C '{domain}'".format(domain=cfg['domain']))


    return {'success': True}
