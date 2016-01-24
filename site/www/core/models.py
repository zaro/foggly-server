from django.db import models
from django.contrib.auth.models import User

# Create your models here.

TASK_STATUS = (
    (1, "New"),
    (2, "Pending"),
    (3, "Progress"),
    (4, "Finished"),
)

TASK_TYPE = (
    (1, "Setup"),
    (2, "Add SSL Support"),
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

class Domain(TimeStampedModel):
    user = models.ForeignKey(User, related_name='+')
    domain_name = models.CharField(max_length=200)
