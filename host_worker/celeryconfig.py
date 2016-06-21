"""
    Default celery configuration for per host worker
"""
from kombu import Exchange, Queue
from kombu.common import Broadcast

# Broker settings.
BROKER_URL = 'redis://192.168.1.111'

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://192.168.1.111'

CELERY_ENABLE_UTC = True

CELERY_IMPORTS = ('host_worker', )

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ENABLE_UTC = True

CELERY_QUEUES = (
    Queue('any_host', Exchange('any_host'), routing_key='any_host.#'),
    Broadcast(name='every_host', queue='every_host', routing_key='every_host.#')
)
CELERY_ROUTES = {'host.dockerStatus': {'queue': 'every_host'}}
