from django.db import models

# Create your models here.
from core.dockerctl import DockerCtl

def getDomainsList(user):
        # Filter for current user
        containersList = DockerCtl().listContainers();
        containers = {}
        statusMap={'exited':'down', 'removal':'down', 'dead':'down'}
        for cont in containersList:
            domain = cont['Names'][0][1:]
            containers[domain] = {
                'domain' : domain,
                'type' : cont['Image'],
                'status' : cont['Status'],
                'created': cont['Created'],
                'state': statusMap[cont['state']] if cont['state'] in statusMap else cont['state'],
            }

        response = []
        for domain in  core.models.DomainModel.objects.filter(user=user):
            if domain.domain_name in containers:
                response.append( containers[domain.domain_name] )
            else :
                response.append({
                    'domain' : domain.domain_name,
                    'type' : domain.app_type.container_id,
                    'status' : 'Exited',
                    'created': None,
                    'state' : 'down'
                })
