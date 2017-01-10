from django.conf.urls import url
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from jwt_auth.views import obtain_jwt_token
import api.views
from api.views_common import missingMethod

import inspect, re

urlpatterns = [
    url(r'^auth$', obtain_jwt_token)
]


def classToPath(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1/\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1/\2', s1).lower()

# append all views with urls as class name
for name in dir(api.views):
    view = getattr(api.views, name)
    if inspect.isclass(view) and issubclass(view, View):
        path = classToPath(name)
        urlpatterns.append(url(path + '$', csrf_exempt( view.as_view() ), name=path)),

# catch all other /api request
urlpatterns.append(url('^.*$', csrf_exempt( missingMethod ))),
