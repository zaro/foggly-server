from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import authenticate, login
from core.forms import DomainForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin).as_view(**initkwargs)
        return login_required(view)

class PermissionsRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PermissionsRequiredMixin).as_view(**initkwargs)
        return permission_required(view)

# Create your views here.
class HomeView(View):
    template_name = 'home_template.html'

    def get(self, request):
        return render(request, self.template_name, {})

class LoginView(View):
    template_name = 'login_template.html'
    form_class = None

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        pass

class PanelView(View):
    template_name = 'domains_template.html'

    def get(self, request):
        return render(request, self.template_name, {})

class DomainAddView(View):
    template_name = 'domain_add_template.html'

    def get(self, request):
        return render(request, self.template_name, {"form": DomainForm()})

    def post(self, request, *args, **kwargs):
        pass
