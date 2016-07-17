from .task_utils import allDomainDirs, DomainConfig
from .tasks import getDockerStatus, startDomain


def startDomains():
    containers = getDockerStatus()
    print('Current containers state:', containers)
    for domainDir in allDomainDirs():
        hostCfg = DomainConfig(domainDir.filename('.hostcfg'))
        if not hostCfg.exists():
            continue
        user = hostCfg.get('OWNER')
        domain = hostCfg.get('DOMAIN')
        status = domainDir.readFile('.domainstate')
        domainState = containers.get(domain).get('state') if containers.get(domain) else 'down'
        print('Domain {}/{} status={} currentState={}'.format(user, domain, status, domainState))
        if status == 'started' and domainState != 'up':
            print('startDomain({}, {})'.format(user, domain))
            startDomain({'user': user, 'domain': domain})

if __name__ == '__main__':
    startDomains()
