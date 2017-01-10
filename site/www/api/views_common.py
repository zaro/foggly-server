import json
from django.http import JsonResponse

import base64
import pickle

from celery.result import result_from_tuple


def makeError(text, data={}):
    return JsonResponse( { 'error': text.format(**data) } )


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


def missingMethod(request):
    return makeError('Method missing')


def taskToId(asyncResult):
    t = asyncResult.as_tuple()
    return base64.urlsafe_b64encode(pickle.dumps(t, -1)).decode()


def taskFromId(id):
    t = pickle.loads(base64.urlsafe_b64decode(id))
    return result_from_tuple(t)


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
