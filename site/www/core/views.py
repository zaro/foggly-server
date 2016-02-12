from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from core.forms import DomainForm, LoginForm

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)

class PermissionsRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return permission_required(view)

# Create your views here.
class HomeView(View):
    template_name = 'home_template.html'

    def get(self, request):
        return render(request, self.template_name, {})

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
        return render(request, self.template_name, {})

class DomainAddView(LoginRequiredMixin, View):
    template_name = 'domain_add_template.html'

    def get(self, request):
        return render(request, self.template_name, {"form": DomainForm()})

    def post(self, request, *args, **kwargs):
        pass

class SettingsView(LoginRequiredMixin, View):
    template_name = 'settings_template.html'

    def get(self, request):
        return render(request, self.template_name, {})
