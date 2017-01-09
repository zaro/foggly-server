"""
    Docker interface module
"""
from docker import Client
from .task_utils import getDomainDir, DomainConfig


import os, tarfile, io


class DockerCtl(Client):
    """
        Simple docker interface class
    """
    def __init__(self, baseUrl):
        super().__init__(base_url=baseUrl)

    def getFileUNFINISHED(self, containerId):
        container = self.create_container(image=containerId, command='/bin/true')
        (tarSteam, stats) = self.get_archive(container, '/etc/')
        print(stats)
        tarFile = io.BytesIO(tarSteam.read())
        tar = tarfile.open(fileobj=tarFile)
        print(tar.extractfile('etc/passwd').read())
        self.remove_container(container, v=True)

    def getWwwDataUser(self, containerId):
        container = self.create_container(image=containerId, command="sh -c \"grep www-data /etc/passwd /etc/group | cut -d ':' -f 4\"")
        self.start( container )
        response = self.logs( container, stdout=True, stderr=True)
        self.remove_container(container, v=True)
        u, g, _ = response.split(b'\n')
        return (int(u), int(g))

    def _stateFromStatus(self, status):
        return status.split(' ')[0].lower()

    def listContainers(self):
        containers = self.containers(all=True)
        for cont in containers:
            cont['state'] = self._stateFromStatus( cont['Status'] )
        return containers

    def getContainerStatus(self, username, domain):
        containers = self.containers(all=True)
        name = '/' + domain
        for container in containers:
            if name in container['Names']:
                # status will be on of ['up, 'exited', 'restarting', 'removal', 'dead']
                # explanation about dead/removal : http://stackoverflow.com/questions/30550472/docker-container-with-status-dead-after-consul-healthcheck-runs
                return self._stateFromStatus( container['Status'] )
        return None

    def stopContainer(self, username, domain, **options):
        self.stop(domain)

    def rmContainer(self, username, domain, **options):
        self.remove_container(domain)

    def runContainer(self, username, domain, containerId, **options):
        domainDir = getDomainDir(username, domain)
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
        host_config = self.create_host_config(
            binds={
                domainDir.getDockerLocation(): {
                    'bind': '/srv/home',
                    'mode': 'rw',
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
            port_bindings={
                22: SSH_PORT,
                3000: WWW_PORT
            },
            mem_limit=(options.get('mem_limit') or '512m'),
        )
        print('runContainer: host_config=' +str(host_config))
        container = self.create_container(
            image=containerId,
            hostname=domain,
            name=domain,
            host_config=host_config,
            environment=cfg.asDict(),
        )
        self.start( container )
