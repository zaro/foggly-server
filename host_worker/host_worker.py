from host_tasks.tasks import *
from celery import Celery

app = Celery('host_worker')
app.config_from_object('celeryconfig')
