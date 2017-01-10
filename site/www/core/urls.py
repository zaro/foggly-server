from django.conf.urls import include, url
from django.contrib import admin
from core.views import (
    HomeView,
    LoginView,
    DomainView,
    DomainAddView,
    LogoutView,
    DatabaseMysqlView,
    DatabasesPostgresView,
)

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^domains/$', DomainView.as_view(), name='domains'),
    url(r'^databases/mysql$', DatabaseMysqlView.as_view(), name='databases-mysql'),
    url(r'^databases/postgres$', DatabasesPostgresView.as_view(), name='databases-postgres'),
    url(r'', HomeView.as_view(), name='home'),
]
