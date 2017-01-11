from __future__ import absolute_import
from celery.schedules import crontab

import os

from celery import Celery
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hosting.settings')

from django.conf import settings  # noqa

app = Celery('hosting_tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'add-every-day-after-midnight': {
        'task': 'core.tasks.certbotRenewAllHosts',
        'schedule': crontab(hour=1, minute=30, day_of_week='*'),
    },
}
