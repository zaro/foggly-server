from django.conf import settings
from docker import Client
from core.task_utils import getDomainDir


from core.task_utils import CfgGen

import os, tarfile, io

class DockerCtl(Client):
    def __init__(self):
        super().__init__(base_url=settings.DOCKER_BASE_URL)

    def getFileUNFINISHED(self, containerId):
        container = self.create_container(image=containerId, command='/bin/true')
        (tarSteam, stats) = self.get_archive(container, '/etc/')
        print (stats)
        tarFile = io.BytesIO(tarSteam.read())
        tar = tarfile.open(fileobj=tarFile)
        print (tar.extractfile('etc/passwd').read())
        self.remove_container(container, v=True)

    def getWwwDataUser(self, containerId):
        container = self.create_container(image=containerId, command="sh -c \"grep www-data /etc/passwd /etc/group | cut -d ':' -f 4\"")
        self.start( container )
        response = self.logs( container, stdout=True, stderr=True)
        self.remove_container(container, v=True)
        u,g,_ = response.split(b'\n')
        return (int(u), int(g))

    def runContainer(self, username, domain, containerId, **options):
        dataDir = getDomainDir(username, domain).path
        if containerId.find(':') < 0:
            containerId += ':latest'
        if not os.path.exists( dataDir ):
            raise Exception('Invalid username and/or domain')
        cfg = CfgGen(os.path.join(dataDir, '.hostcfg'))
        try:
            WWW_PORT=int(cfg.get('WWW_PORT'))
            SSH_PORT=int(cfg.get('SSH_PORT'))
        except:
            raise Exception('Invalid port configuration for domain')
        volumes=[dataDir, '/var/lib/mysql/'],
        host_config=self.create_host_config(
            binds={
                dataDir : {
                    'bind': '/srv/home',
                    'mode': 'rw',
                },
                '/var/lib/mysql/': {
                    'bind': '/var/lib/mysql/',
                    'mode': 'ro',
                }
            },
            port_bindings={
                22: SSH_PORT,
                80: WWW_PORT
            },
            mem_limit=(options.get('mem_limit') or '128m'),
        )
        container = self.create_container(
            image=containerId, hostname=domain,
            #volumes=volumes,
            #ports=[22, 80],
            host_config=host_config,
        )
        self.start( container )
