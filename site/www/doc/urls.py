from django.conf.urls import include, url
from django.contrib import admin
from doc.views import DocBaseView

urlpatterns = [
    url(r'^(?P<templateName>.*)$', DocBaseView.as_view()),
]
