from django.shortcuts import render, redirect
from django.views.generic import View
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.mixins import LoginRequiredMixin

from core.forms import (
    DomainForm,
    LoginForm,
    DatabaseForm,
)
from core.models import (
    ContainerRuntime,
    Host,
)


# Create your views here.
class HomeView(View):

    def get(self, request):
        template_name = 'home_template.html'
        templateVars = {}
        if request.user.is_authenticated():
            template_name = 'dashboard_template.html'
        return render(request, template_name, templateVars)


class LoginView(View):
    template_name = 'login_template.html'

    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
            # return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return redirect(settings.LOGIN_URL)

        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password'))

        if user is not None and user.is_active:
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

        return redirect(settings.LOGIN_URL)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect(settings.LOGIN_URL)


class DomainView(LoginRequiredMixin, View):
    template_name = 'domains_template.html'

    def get(self, request):
        return render(request, self.template_name, {
            'appTypes': ContainerRuntime.objects.all(),
            'hosts': Host.objects.all(),
        })


class DomainAddView(LoginRequiredMixin, View):
    template_name = 'domain_add_template.html'

    def get(self, request):
        return render(request, self.template_name, {"form": DomainForm()})

    def post(self, request, *args, **kwargs):
        pass


class DatabaseMysqlView(LoginRequiredMixin, View):
    template_name = 'dbs_template.html'

    def get(self, request):
        return render(request, self.template_name, {
            'appTypes': ContainerRuntime.objects.all(),
            'hosts': Host.objects.all(),
            'react_bundle': 'databasesmysqlpage',
        })


class DatabasesPostgresView(LoginRequiredMixin, View):
    template_name = 'dbs_template.html'

    def get(self, request):
        return render(request, self.template_name, {
            'appTypes': ContainerRuntime.objects.all(),
            'hosts': Host.objects.all(),
            'react_bundle': 'databasespostgrespage',
        })
