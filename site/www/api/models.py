from django.db import models

# Create your models here.
from core.dockerctl import DockerCtl

def getDomainsList(user):
        # Filter for current user
        containersList = DockerCtl().listContainers();
        containers = {}
        for cont in containersList:
            containers[cont['domain']] = cont

        response = []
        for domain in  core.models.DomainModel.objects.filter(user=user):
            if domain.domain_name in containers:
                response.append( containers[domain.domain_name] )
            else :
                response.append({
                    'domain' : domain.domain_name,
                    'type' : domain.app_type.container_id,
                    'status' : 'exited',
                    'created': None,
                    'state' : 'down'
                })
