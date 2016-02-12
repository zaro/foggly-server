from django.conf.urls import include, url
from django.contrib import admin
from core.views import (
    HomeView,
    LoginView,
    DomainView,
    DomainAddView,
    LogoutView,
    SettingsView,
)

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^domains/$', DomainView.as_view(), name='domains'),
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^domains/add/$', DomainAddView.as_view(), name='domain_add'),
    url(r'', HomeView.as_view(), name='home'),
]
