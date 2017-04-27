from django.contrib import admin
from core import models


@admin.register(models.DomainModel)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['user', 'domain_name', 'app_type', 'host']


class ContainerAdmin(admin.ModelAdmin):
    list_display = ['container_id', 'description']


class SharedDatabaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'db_user', 'db_pass', 'db_name', 'db_type', 'host']


class HostAdmin(admin.ModelAdmin):
    list_display = ['description', 'main_domain']


@admin.register(models.DomainConfig)
class DomainConfig(admin.ModelAdmin):
    list_display = ['domain', 'key', 'value']


# Register your models here.
admin.site.register(models.ContainerRuntime, ContainerAdmin)
admin.site.register(models.SharedDatabase, SharedDatabaseAdmin)
admin.site.register(models.Host, HostAdmin)
