from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyField

from core.dockerctl import DockerCtl

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

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self.to_dict()) + ')'

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(self)
        return data

    class Meta:
        abstract = True

class DockerContainer(TimeStampedModel):
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
