from django.http import JsonResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import core.models
import core.hostjobs


from api.mixins import ApiLoginRequiredMixin
import api.base_views as base_views
from api.views_common import handleExceptions, mandatoryParams, parseJson, makeError, taskToId, taskFromId

from celery.exceptions import TimeoutError
import redis

import logging
log = logging.getLogger('api')

redisPool = None


def getRedisConnection():
    global redisPool
    if redisPool is None:
        redisPool = redis.ConnectionPool.from_url(settings.REDIS_URL)
    return redis.StrictRedis(connection_pool=redisPool)


# Task polling
class Task(ApiLoginRequiredMixin, View):
    def get(self, request):
        taskId = request.GET.get('id', None )
        timeout = request.GET.get('timeout', '60' )
        try:
            timeoutSeconds = int(timeout)
        except ValueError:
            pass
        if timeoutSeconds < 1 or timeoutSeconds > 1800:
            timeoutSeconds = 60
        if not taskId:
            return JsonResponse( { 'error': 'Invalid task id: {}'.format(taskId) } )
        try:
            result = taskFromId(taskId)
            log.info("Task {taskId} status is: {status}".format(taskId=taskId, status=result.status))
            log.info("Task {taskId} parent: {parent}".format(taskId=taskId, parent=result.parent))
            result.get(timeout=timeoutSeconds, interval=0.5)
        except TimeoutError:
            return JsonResponse( { 'completed': False, 'response': None } )
        except Exception as e:
            log.warn("Task failed with exception:" + str(e))
            return JsonResponse( { 'completed': True, 'status': result.status, 'error': str(e) } )
        s = result.result
        log.info(" > " + str(type(s)) + ":" + str(s))
        if type(s) is dict and s.get('error'):
            return JsonResponse( { 'completed': True, 'status': result.status, 'error': s.get('error') } )
        return JsonResponse( { 'completed': True, 'status': result.status, 'response': result.result } )


# Domains controller
class Domains(ApiLoginRequiredMixin, View):
    def getHostContainers(self, hosts):
        containers = {}
        if len(hosts) == 0:
            return containers
        try:
            r = getRedisConnection()
            hostKeys = [ 'dockerStatus:' + host for host in hosts ]
            dockerStatuses = r.mget(hostKeys)
            for host in hosts:
                stat = dockerStatuses.pop(0)
                containers[host] = parseJson(stat) if stat else {}
        except:
            pass
        return containers

    def get(self, request):
        """
            Return  list with current user domains , for each domain :
            {
                'domain' : 'example.com' , # The domain name
                'type' : 'foggly/php7', # image type
                'status' : 'up', # status, one of ['up', 'down', 'restarting']
                'created': unix Epoch time, # container start time
            }

        """
        # Filter for current user
        response = []
        domains = core.models.DomainModel.objects.filter(user=request.user)
        containersPerHost = self.getHostContainers([ domain.host.main_domain for domain in domains if domain.host ])
        for domain in domains:
            if not domain.host:
                continue
            containers = containersPerHost.get(domain.host.main_domain)
            if containers and domain.domain_name in containers:
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
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).start(
            {'user': user.username, 'domain': domain.domain_name}
        )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })

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
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).stop(
            {'user': user.username, 'domain': domain.domain_name}
        )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DomainsConfig(ApiLoginRequiredMixin, View):
    def get(self, request):
        """
            Return  list with current domains configuration, for each domain :
            {
                'domain' : 'example.com' , # The domain name
                'type' : 'foggly/php7', # image type
                'config' : { dictionary with config variables }
            }

        """
        domains = request.GET.getlist('domain', [] )
        # Filter for current user
        response = []
        domains = core.models.DomainModel.objects.filter(user=request.user, domain_name__in=domains)
        for domain in domains:
            config = {}
            for dc in domain.domainconfig_set.all():
                config[dc.key] = dc.value
            response.append({
                'domain': domain.domain_name,
                'type': domain.app_type.container_id,
                'config': config,
                'sshUrl': 'ssh://{}:{}'.format(config.get('DOMAIN'), config.get('SSH_PORT'))
            })
        return JsonResponse( {'response': response } )


class DomainsAdd(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        reqData = mandatoryParams(reqData, 'domain', 'app_type', 'host')
        # Filter for current user
        user = request.user
        try:
            core.models.DomainModel.objects.get( domain_name=reqData['domain'] )
            return makeError( 'Domain already exists: {domain}', reqData )
        except ObjectDoesNotExist:
            pass
        try:
            host = core.models.Host.objects.get( main_domain=reqData['host'] )
        except ObjectDoesNotExist:
            return makeError( 'Host does not exists: {host}', reqData )
        try:
            app_type = core.models.ContainerRuntime.objects.get( container_id=reqData['app_type'] )
        except ObjectDoesNotExist:
            return makeError( 'app_type does not exists: {host}', reqData )
        reqData['app_type'] = app_type.to_dict(json=True)
        res = core.hostjobs.DomainJobs(host.main_domain, user.username).create( reqData )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DomainsSsl(ApiLoginRequiredMixin, View):
    def get(self, request):
        """
            Return  list with true/false for each domain ssl status, for each domain :
        """
        domains = request.GET.getlist('domain', [] )
        # Filter for current user
        response = []
        domains = core.models.DomainModel.objects.filter(user=request.user, domain_name__in=domains)
        for domain in domains:
            response.append({
                'domain': domain.domain_name,
                'hasSsl': domain.domainconfig_set.filter(key='HAS_SSL').last()
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
        except core.models.DomainModel.DoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).enableSsl( reqData )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DomainsRecreate(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        reqData = mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = request.user
        try:
            domain = core.models.DomainModel.objects.get( domain_name=reqData['domain'] )
        except ObjectDoesNotExist:
            return makeError( "Domain doesn't exist exists: {domain}", reqData )
        if not domain.host:
            return makeError( 'Domain [{domain}] has no host attached.', reqData )
        reqData['host'] = domain.host.main_domain
        reqData['app_type'] = domain.app_type.to_dict(json=True)
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).create( reqData )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DomainsDelete(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain')
        # Filter for current user
        user = request.user
        reqData['user'] = user.username
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        if not domain.host:
            return makeError( 'Domain [{domain}] has no host attached.', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).remove( reqData )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DomainsPublickey(ApiLoginRequiredMixin, View):
    @handleExceptions
    def put(self, request):
        reqData = parseJson(request.body)
        mandatoryParams(reqData, 'domain', 'publicKey')
        # Filter for current user
        user = request.user
        reqData['user'] = user.username
        try:
            domain = core.models.DomainModel.objects.get(domain_name=reqData['domain'], user=user)
        except ObjectDoesNotExist:
            return makeError( 'Invalid domain id: {domain}', reqData )
        if not domain.host:
            return makeError( 'Domain [{domain}] has no host attached.', reqData )
        res = core.hostjobs.DomainJobs(domain.host.main_domain, user.username).addPublicKey( reqData )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


# Database APIs
class DatabasesMysql(base_views.DatabasesBase):
    DB_TYPE = 'mysql'


class DatabasesMysqlAdd(base_views.DatabasesBaseAdd):
    DB_TYPE = 'mysql'


class DatabasesMysqlDelete(base_views.DatabasesBaseDelete):
    DB_TYPE = 'mysql'


class DatabasesPostgres(base_views.DatabasesBase):
    DB_TYPE = 'postgres'


class DatabasesPostgresAdd(base_views.DatabasesBaseAdd):
    DB_TYPE = 'postgres'


class DatabasesPostgresDelete(base_views.DatabasesBaseDelete):
    DB_TYPE = 'postgres'
