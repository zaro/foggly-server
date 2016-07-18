from django.shortcuts import render, redirect
from django.views.generic import View
from core.models import SharedDatabase, DomainModel, DomainConfig, DockerContainer, Host
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
class DocBaseView(View):

    def get(self, request, templateName):
        domain = request.GET.get('forDomain', None)
        try:
            domainInstance = DomainModel.objects.get(domain_name=domain)
        except ObjectDoesNotExist:
            domainInstance = None

        return render(request, templateName + '.md', {
            'domain': domainInstance,
        })
