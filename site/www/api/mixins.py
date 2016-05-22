from django.http import HttpResponse
from django.contrib.auth.mixins import AccessMixin
from jwt_auth.mixins import JSONWebTokenAuthMixin
from jwt_auth import exceptions
import json


class ApiLoginRequiredMixin(AccessMixin, JSONWebTokenAuthMixin):
    """
    Mixin which verifies that the current user is authenticated or has valid web token
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            acceptsHtml = False
            for t in request.META.get('HTTP_ACCEPT').split(','):
                t = t.lower()
                if t.startswith('text/html') or t.startswith('application/xhtml+xml'):
                    acceptsHtml = True
                    break
            if not acceptsHtml:
                try:
                    request.user, request.token = self.authenticate(request)
                except exceptions.AuthenticationFailed as e:
                    response = HttpResponse(
                        json.dumps({'error': str(e)}),
                        status=401,
                        content_type='application/json'
                    )
                    response['WWW-Authenticate'] = self.authenticate_header(request)
                    return response
            else:
                return self.handle_no_permission()
        return super(JSONWebTokenAuthMixin, self).dispatch(request, *args, **kwargs)
