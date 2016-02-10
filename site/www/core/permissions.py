from core.models import DomainModel
from django.contrib.auth.models import Permissions
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_from_model(DomainModel)
permission = Permissions.objects.create(content_type=content_type)
