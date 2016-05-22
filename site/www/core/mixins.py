from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
import json


class PermissionsRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return permission_required(view)


class JsonResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return json.dumps(context)
