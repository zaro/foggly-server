"""
    Default celery configuration for per host worker
"""
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
