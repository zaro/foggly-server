from django.conf.urls import include, url
from django.contrib import admin
from core.views import HomeView, LoginView, PanelView, DomainAddView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^domains/$', PanelView.as_view(), name='domains'),
    url(r'^domains/add/$', DomainAddView.as_view(), name='domain_add'),
    url(r'', HomeView.as_view(), name='home'),
]
