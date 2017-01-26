"""
    Docker interface module
"""
import docker
from .task_utils import getDomainDir, DomainConfig


class DockerCtl:
    """
        Simple docker interface class
    """
    _statusMap = {'exited': 'down', 'removal': 'down', 'dead': 'down', 'running': 'up', 'created': 'up'}

    def __init__(self, baseUrl=None):
        if not baseUrl:
            baseUrl = 'unix://host_run/docker.sock'
        self.client = docker.DockerClient(base_url=baseUrl)

    def _stateFromStatus(self, status):
        return self._statusMap.get(status, status)

    def listContainers(self):
        containers = self.client.containers.list(all=True)
        result = []
        for cont in containers:
            result.append({
                'domain': cont.name,
                'type': cont.attrs['Config']['Image'],
                'status': cont.status,
                'created': cont.attrs['Created'],
                'state': self._stateFromStatus(cont.status),
            })
        return result

    def getContainerState(self, username, domain):
        try:
            container = self.client.containers.get(domain)
            return self._stateFromStatus(container.status)
        except docker.errors.NotFound:
            return None

    def stopContainer(self, username, domain, **options):
        container = self.client.containers.get(domain)
        container.stop()

    def rmContainer(self, username, domain, **options):
        container = self.client.containers.get(domain)
        container.remove()

    def runContainer(self, username, domain, containerId, **options):
        domainDir = getDomainDir(username, domain)
        logDir = domainDir.clone().pushd('log')
        if not domainDir.exists():
            raise Exception('Invalid username and/or domain')
        if containerId.find(':') < 0:
            containerId += ':latest'
        cfg = DomainConfig(domainDir.filename('.hostcfg'))
        try:
            WWW_PORT = int(cfg.get('WWW_PORT'))
            SSH_PORT = int(cfg.get('SSH_PORT'))
        except:
            raise Exception('Invalid port configuration for domain')
        # Stopping docker container with systed inside :
        #  https://bugzilla.redhat.com/show_bug.cgi?id=1201657
        #  https://rhn.redhat.com/errata/RHEA-2016-1057.html
        self.client.containers.run(
            detach=True,
            image=containerId,
            hostname=domain,
            name=domain,
            environment=cfg.asDict(),
            cap_add=['SYS_ADMIN'],
            stop_signal='RTMIN+3',
            mem_limit=(options.get('mem_limit') or '1024m'),
            ports={
                22: SSH_PORT,
                3000: WWW_PORT
            },
            volumes={
                domainDir.getDockerLocation(): {
                    'bind': '/srv/home',
                    'mode': 'rw',
                },
                logDir.getDockerLocation(): {
                    'bind': '/var/log',
                    'mode': 'rw',
                },
                '/sys/fs/cgroup': {
                    'bind': '/sys/fs/cgroup',
                    'mode': 'ro'
                },
                '/var/lib/mysql/': {
                    'bind': '/var/lib/mysql/',
                    'mode': 'ro',
                },
                '/var/run/postgresql/': {
                    'bind': '/var/run/postgresql/',
                    'mode': 'ro',
                }
            },
        )

# if __name__ == '__main__':
#     import time
#     d = DockerCtl()
#     print(d.listContainers())
#     container = d.client.containers.get('test2.domain')
#     print(container.attrs['Config']['Image'])
    # d.runContainer('admin', 'test2.domain', 'foggly/nodejs')
    # print(d.listContainers())
    # time.sleep(10)
    # d.stopContainer('admin', 'test2.domain')
    # time.sleep(3)
    # d.rmContainer('admin', 'test2.domain')
