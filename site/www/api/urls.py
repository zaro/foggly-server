from django.conf.urls import include, url
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import api.views
import inspect

urlpatterns = [
]

for name in dir(api.views):
    view = getattr(api.views, name)
    if inspect.isclass(view) and issubclass(view, View):
        path = name.lower()
        urlpatterns.append(url(path+'$', csrf_exempt( view.as_view() ), name=path)),
