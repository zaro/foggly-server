from django.db import models
from django.contrib.auth.models import User

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

class DomainModel(TimeStampedModel):
    user = models.ForeignKey(User, related_name='+')
    domain_name = models.CharField(max_length=200)
    app_type = models.CharField(max_length=20, choices=APP_TYPES, default="php7-mysql")

class DockerImage(models.Model):
    pass

class DockerContainer(models.Model):
    pass
