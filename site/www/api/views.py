from django.http import JsonResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist

import core.models
from core.hosttasks import *  # noqa
import core.hostjobs

from api.mixins import ApiLoginRequiredMixin

from celery.result import AsyncResult
import json

import logging
log = logging.getLogger('api')


class InvalidJson(Exception):
    def __init__(self, error):
        super().__init__('Invalid json [{}]'.format(error))


class InvalidParam(Exception):
    def __init__(self, param, value):
        super().__init__('Invalid value for parameter [{}]:[{}]'.format(param, value))


def parseJson(body):
    # logger.debug('Parsing:' + body.decode('utf8'))
    if len(body) == 0:
        raise InvalidJson('Empty')
    try:
        return json.loads(body.decode('utf8'), encoding='utf8')
    except ValueError as e:
        raise InvalidJson(e)


def mandatoryParams(reqData, *params):
    out = {}
    for param in params:
        if reqData.get(param) is None:
            raise InvalidParam(param, None)
        out[param] = reqData.get(param)
    return out


def handleExceptions(method):
    def _handler(self, request):
        try:
            return method(self, request)
        except InvalidParam as e:
            return JsonResponse( { 'error': str(e) } )
        except InvalidJson as e:
            return JsonResponse( { 'error': str(e) } )
    return _handler


def makeError(text, data={}):
    return JsonResponse( { 'error': text.format(**data) } )


def missingMethod(request):
    return makeError('Method missing')


# Task polling
class Task(ApiLoginRequiredMixin, View):
    def get(self, request):
        taskId = request.GET.get('id', None )
        if not taskId:
            return JsonResponse( { 'error': 'Invalid task id: {}'.format(taskId) } )
        result = AsyncResult(taskId)
        if not result.ready():
            return JsonResponse( { 'completed': False, 'response': None } )
        return JsonResponse( { 'completed': True, 'response': result.get(), 'status': result.status } )


# Domains controller
class Domains(ApiLoginRequiredMixin, View):
    def getHostContainers(self, host):
        dockerUrl = 'tcp://{}:{}'.format(host.controller_ip, host.docker_port)
        containersList = DockerCtl(dockerUrl).listContainers()
        containers = {}
        statusMap = {'exited': 'down', 'removal': 'down', 'dead': 'down'}
        for cont in containersList:
            domain = cont['Names'][0][1:]
            containers[domain] = {
                'domain': domain,
                'type': cont['Image'],
                'status': cont['Status'],
                'created': cont['Created'],
                'state': statusMap[cont['state']] if cont['state'] in statusMap else cont['state'],
            }
        return containers

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
        containersPerHost = {}
        response = []
        for domain in core.models.DomainModel.objects.filter(user=request.user):
            host = domain.host
            if host is None:
                continue
            containers = containersPerHost.get(host.main_domain)
            if not containers:
                containers = self.getHostContainers(host)
                containersPerHost[host.main_domain] = containers
            if domain.domain_name in containers:
                response.append( containers[domain.domain_name] )
            else:
                response.append({
                    'domain': domain.domain_name,
                    'type': domain.app_type.container_id,
                    'status': 'Exited',
                    'created': None,
                    'state': 'down'
                })

        return JsonResponse( {'response': response } )

    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = request.user
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain).startDomain(
            {'user': user.username, 'domain': domain.domain_name}
        )
        return JsonResponse({ 'completed': False, 'id': res.id })

    @handleExceptions
    def delete(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = request.user
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain).stopDomain(
            {'user': user.username, 'domain': domain.domain_name}
        )
        return JsonResponse({ 'completed': False, 'id': res.id })


class DomainsAdd(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        reqData = mandatoryParams(reqData, 'domain', 'app_type', 'host')
        # Filter for current user
        reqData['user'] = request.user.username
        try:
            core.models.DomainModel.objects.get( domain_name=reqData['domain'] )
            return makeError( 'Domain already exists: {domain}', reqData )
        except ObjectDoesNotExist:
            pass
        try:
            host = core.models.Host.objects.get( main_domain=reqData['host'] )
        except ObjectDoesNotExist:
            return makeError( 'Host does not exists: {host}', reqData )

        res = core.hostjobs.DomainJobs(host.main_domain).create( reqData )
        log.debug('domain/add taks -> %s', res)
        return JsonResponse({ 'completed': False, 'id': res.id })


class DomainsDelete(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = request.user
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        if not domain.host:
            return makeError( 'Domain [{domain}] has no host attached.', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain).remove( reqData )
        return JsonResponse({ 'completed': False, 'id': res.id })


# Create your views here.
class DatabasesMysql(ApiLoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        response = []
        for database in core.models.SharedDatabase.objects.filter(user=user, db_type='mysql'):
            response.append(database.to_dict())
        return JsonResponse( {'response': response } )


class DatabasesMysqlAdd(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'db_user', 'db_pass', 'db_name', 'host')
        params['user'] = request.user.username
        try:
            host = core.models.host.objects.get( main_domain=reqData['host'] )
        except ObjectDoesNotExist:
            return makeError( 'Host does not exists: {host}', reqData )
        res = core.hostjobs.MysqlJobs(host.main_domain).create( reqData )
        return JsonResponse({ 'completed': False, 'id': res.id })


class DatabasesMysqlDelete(ApiLoginRequiredMixin, View):
    @handleExceptions
    def delete(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'db_user', 'db_name', 'host')
        params['user'] = request.user.username
        try:
            host = core.models.Host.objects.get( main_domain=reqData['host'] )
        except ObjectDoesNotExist:
            return makeError( 'Host does not exists: {host}', reqData )
        res = core.hostjobs.MysqlJobs(host.main_domain).remove( reqData )
        return JsonResponse({ 'completed': False, 'id': res.id })
