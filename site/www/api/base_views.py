from django.views.generic import View
from api.mixins import ApiLoginRequiredMixin
from django.http import JsonResponse

import core.models
import core.hostjobs

from api.views_common import handleExceptions, mandatoryParams, parseJson, makeError, taskToId


class DatabasesBase(ApiLoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        response = []
        for database in core.models.SharedDatabase.objects.filter(user=user, db_type=self.DB_TYPE):
            d = database.to_dict()
            d['host'] = database.host.main_domain
            response.append(d)
        return JsonResponse( {'response': response } )


class DatabasesBaseAdd(ApiLoginRequiredMixin, View):
    @handleExceptions
    def post(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'db_user', 'db_pass', 'db_name', 'host')
        params['user'] = request.user.username
        try:
            host = core.models.Host.objects.get( main_domain=params['host'] )
        except core.models.Host.DoesNotExist:
            return makeError( 'Host does not exists: {host}', params )
        params['db_type'] = self.DB_TYPE
        res = core.hostjobs.DatabaseJobs(host.main_domain).create( params )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })


class DatabasesBaseDelete(ApiLoginRequiredMixin, View):
    @handleExceptions
    def delete(self, request):
        reqData = parseJson(request.body)
        params = mandatoryParams(reqData, 'db_user', 'db_name', 'host')
        params['user'] = request.user.username
        try:
            host = core.models.Host.objects.get( main_domain=params['host'] )
        except core.models.Host.DoesNotExist:
            return makeError( 'Host does not exists: {host}', params )
        params['db_type'] = self.DB_TYPE
        res = core.hostjobs.DatabaseJobs(host.main_domain).remove( params )
        return JsonResponse({ 'completed': False, 'id': taskToId(res) })
