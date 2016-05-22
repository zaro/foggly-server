from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ManyToManyField
from django.core.validators import MaxValueValidator, MinValueValidator

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


class Host(TimeStampedModel):
    ip = models.GenericIPAddressField(unpack_ipv4=True)
    main_domain = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    controller_ip = models.GenericIPAddressField(unpack_ipv4=True)
    docker_port = models.IntegerField(
        default=2375,
        validators=[
            MaxValueValidator(65535),
            MinValueValidator(1)
        ]
    )

    def _visibleName(self):
        return self.description


class DockerContainer(TimeStampedModel):
    container_id = models.CharField(max_length=100, default="zaro/php7")
    description = models.CharField(max_length=200, default="Apache 2.4 / PHP 7.0")
    proxy_type = models.CharField(max_length=50, choices=PROXY_TYPES, default="http")

    def _visibleName(self):
        return self.description


class DomainModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    host = models.ForeignKey(Host, on_delete=models.SET_NULL, null=True, related_name='+')
    domain_name = models.CharField(max_length=200)
    app_type = models.ForeignKey(
        DockerContainer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def _visibleName(self):
        return self.domain_name


class SharedDatabase(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    host = models.ForeignKey(Host, on_delete=models.SET_NULL, null=True, related_name='+')
    db_user = models.CharField(max_length=50)
    db_pass = models.CharField(max_length=50)
    db_name = models.CharField(max_length=50)
    db_type = models.CharField(max_length=50, choices=DATABASE_TYPES)

    def _visibleName(self):
        return self.db_user + '@' + self.db_name


class DockerImage(models.Model):
    pass
