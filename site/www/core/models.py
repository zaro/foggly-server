from django.db import models
from django.contrib.auth.models import User

from core.dockerctl import DockerCtl

# Create your models here.
# TASK_STATUS = (
#     (1, "New"),
#     (2, "Pending"),
#     (3, "Progress"),
#     (4, "Finished"),
# )
#
# TASK_TYPE = (
#     (1, "Setup"),
#     (2, "Add SSL Support"),
# )

PROXY_TYPES = (
    ("http", "HTTP"),
    ("uwsgi", "uWSGI"),
    ("fastcgi", "FastCGI"),
)

DATABASE_TYPES = (
    ("mysql", "MySQL"),
    ("postgre", "PostgreSQL"),
    ("mongo", "Mongo"),
    ("couchdb", "CouchDB"),
)

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    . fields. updating ``created`` and ``modified``
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DockerContainer(models.Model):
    container_id = models.CharField(max_length=100, default="zaro/php7")
    description = models.CharField(max_length=200, default="Apache 2.4 / PHP 7.0")
    proxy_type = models.CharField(max_length=50, choices=PROXY_TYPES, default="http")

class DomainModel(TimeStampedModel):
    user = models.ForeignKey(User, related_name='+')
    domain_name = models.CharField(max_length=200)
    app_type = models.ForeignKey(
        DockerContainer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

class SharedDatabase(TimeStampedModel):
    user = models.ForeignKey(User, related_name='+')
    db_user = models.CharField(max_length=50)
    db_pass = models.CharField(max_length=50)
    db_name = models.CharField(max_length=50)
    db_type = models.CharField(max_length=50, choices=DATABASE_TYPES)

class DockerImage(models.Model):
    pass
