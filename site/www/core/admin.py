from django.contrib import admin
from core import models
from django_object_actions import DjangoObjectActions

class DomainAdmin(DjangoObjectActions, admin.ModelAdmin):

    def create_domain(self, request, obj):
        pass
    create_domain.label = "Create structure"
    create_domain.short_description = "Run create domain layout structure"
    objectactions = ('create_domain',)
    list_display = ['user', 'domain_name', 'app_type']

class ContainerAdmin(admin.ModelAdmin):
    list_display = ['container_id', 'description']

# Register your models here.
admin.site.register(models.DomainModel, DomainAdmin)
admin.site.register(models.DockerContainer, ContainerAdmin)
