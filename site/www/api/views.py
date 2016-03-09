from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.models import User
from core.dockerctl import DockerCtl
import core.models
from core.tasks import *

from api.mixins import ApiLoginRequiredMixin

from celery.result import AsyncResult
import json

import logging
logger = logging.getLogger('api')

class InvalidJson(Exception):
    def __init__(self, error):
        super().__init__('Invalid json [{}]'.format(error))

class InvalidParam(Exception):
    def __init__(self, param, value):
        super().__init__('Invalid value for parameter [{}]:[{}]'.format(param, value))

def parseJson(body):
    #logger.debug('Parsing:' + body.decode('utf8'))
    if len(body) == 0:
        raise InvalidJson('Empty')
    try:
        return json.loads(body.decode('utf8'), encoding='utf8')
    except ValueError as e:
        raise InvalidJson(e)


def mandatoryParams(reqData, *params):
    out = {}
    for param in params:
        if reqData.get(param) == None:
            raise InvalidParam(param, None)
        out[param] = reqData.get(param)
    return out

def handleExceptions(method):
    def _handler(self, request):
        try:
            return method(self, request)
        except InvalidParam as e :
            return JsonResponse( { 'error': str(e) } )
        except InvalidJson as e :
            return JsonResponse( { 'error': str(e) } )
    return _handler

# Task polling
class Task(ApiLoginRequiredMixin, View):
    def get(self, request):
        taskId = request.GET.get('id', None )
        if not taskId:
            return JsonResponse( { 'error': 'Invalid task id: {}'.format(taskId) } )
        result = AsyncResult(taskId)
        if not result.ready():
            return JsonResponse( { 'completed': False, 'response': None } )
        return JsonResponse( { 'completed': True, 'response': result.get() , 'status': result.status } )

# Domains controller
class Domains(ApiLoginRequiredMixin, View):
    def get(self, request):
        """
            Return  list with current user domains , for each domain :
            {
                'domain' : 'example.com' , # The domain name
                'type' : 'zaro/php7', # image type
                'status' : 'up', # status, one of ['up', 'down', 'restarting']
                'created': unix Epoch time, # container start time
            }

        """
        # Filter for current user
        user = User.objects.get(username='admin')
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
            logger.debug('D:' + str(domain.to_dict()))
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

        return JsonResponse( {'response': response } )

    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = User.objects.get(username='admin')
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return JsonResponse( { 'error': 'Invalid domain id: {}'.format(reqData['domain']) } )
        res = startDomain.delay({'user': user.username, 'domain': domain.domain_name})
        return JsonResponse({ 'completed': False, 'id': res.id })

    @handleExceptions
    def delete(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = User.objects.get(username='admin')
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return JsonResponse( { 'error': 'Invalid domain id: {}'.format(reqData['domain']) } )
        res = stopDomain.delay({'user': user.username, 'domain': domain.domain_name})
        return JsonResponse({ 'completed': False, 'id': res.id })

class DomainsAdd(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        reqData = mandatoryParams(reqData, 'domain', 'app_type')
        # Filter for current user
        reqData['user'] = request.user.username
        try:
            domain = core.models.DomainModel.objects.get( domain_name=reqData['domain'] )
            return JsonResponse( { 'error': 'Domain already exists: {}'.format(reqData['domain']) } )
        except ObjectDoesNotExist:
            pass
        res = createDomain.delay(reqData)
        return JsonResponse({ 'completed': False, 'id': res.id })

class DomainsDelete(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = User.objects.get(username='admin')
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return JsonResponse( { 'error': 'Invalid domain id: {}'.format(reqData['domain']) } )
        res = startDomain.delay({'user': user.username, 'domain': domain.domain_name})
        return JsonResponse({ 'completed': False, 'id': res.id })

# Create your views here.
class MysqlDatabase(ApiLoginRequiredMixin, View):
    def get(self, request):
        # Filter for current user
        user = User.objects.get(username='admin')
        response = []
        for database in  core.models.SharedDatabase.objects.filter(user=user, db_type='mysql'):
            response.append(database.to_dict())
        return JsonResponse( {'response': response } )

    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'mysql_user', 'mysql_password', 'mysql_db')
        # Filter for current user
        user = User.objects.get(username='admin')
        params['user'] = user.username
        res = addMysqlDatabase.delay(params)
        return JsonResponse({ 'completed': False, 'id': res.id })

    @handleExceptions
    def delete(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'mysql_user', 'mysql_db')
        # Filter for current user
        user = User.objects.get(username='admin')
        params['user'] = user.username
        res = removeMysqlDatabase.delay(params)
        return JsonResponse({ 'completed': False, 'id': res.id })
