from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyField
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

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

    def _visibleName(self):
        return self.__class__.__name__ + ' model object'

    def __unicode__(self):
        return self._visibleName()

    def __str__(self):
        return self._visibleName()

    def __repr__(self):
        return self.__class__.__name__ + '$(' + str(self.to_dict()) + ')'

    def to_dict(self, json=False):
        opts = self._meta
        data = {}

        def jsonize(v):
            if not json:
                return v
            if type(v) in [datetime.datetime, datetime.date, datetime.time]:
                return v.isoformat()
            return v
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = [jsonize(v) for v in f.value_from_object(self).values_list('pk', flat=True)]
            else:
                data[f.name] = jsonize(f.value_from_object(self))
        return data

    class Meta:
        abstract = True


class Host(TimeStampedModel):
    main_domain = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def _visibleName(self):
        return self.description


class ContainerRuntime(TimeStampedModel):
    container_id = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    proxy_type = models.CharField(max_length=50, choices=PROXY_TYPES, default="http")

    def _visibleName(self):
        return self.description


class DomainModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    host = models.ForeignKey(Host, on_delete=models.SET_NULL, null=True, related_name='+')
    domain_name = models.CharField(max_length=200)
    app_type = models.ForeignKey(
        ContainerRuntime,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def _visibleName(self):
        return self.domain_name


class DomainConfig(TimeStampedModel):
    domain = models.ForeignKey(DomainModel, on_delete=models.CASCADE)
    key = models.CharField(max_length=256)
    value = models.CharField(max_length=8192)

    def _visibleName(self):
        return self.key + '=' + self.value


class SharedDatabase(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    host = models.ForeignKey(Host, on_delete=models.SET_NULL, null=True, related_name='+')
    db_user = models.CharField(max_length=50)
    db_pass = models.CharField(max_length=50)
    db_name = models.CharField(max_length=50)
    db_type = models.CharField(max_length=50, choices=DATABASE_TYPES)

    def _visibleName(self):
        return self.db_user + '@' + self.db_name
