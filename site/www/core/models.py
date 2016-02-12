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

APP_TYPES = (
    ("php7-mysql", "PHP 7 / MySQL"),
    ("php7-postgre", "PHP 7 / PostgreSQL"),
    ("flask-mongo", "Flask / Mongo"),
    ("django-postgre", "Django / PostgreSQL"),
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

class DomainModel(TimeStampedModel):
    user = models.ForeignKey(User, related_name='+')
    domain_name = models.CharField(max_length=200)
    app_type = models.OneToOneField(
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
    db_type = models.CharField(max_length=50)

class DockerImage(models.Model):
    pass
