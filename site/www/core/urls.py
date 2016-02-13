from django.conf.urls import include, url
from django.contrib import admin
from core.views import (
    HomeView,
    LoginView,
    DomainView,
    DomainAddView,
    LogoutView,
    DatabaseView,
    DatabaseAddView,
)

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^domains/$', DomainView.as_view(), name='domains'),
    url(r'^dbs/$', DatabaseView.as_view(), name='dbs'),
    url(r'^dbs_add/$', DatabaseAddView.as_view(), name='dbs_add'),
    url(r'^domains/add/$', DomainAddView.as_view(), name='domain_add'),
    url(r'', HomeView.as_view(), name='home'),
]
