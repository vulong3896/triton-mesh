import os

from celery import Celery
from kombu import Queue
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mesh.settings')
django.setup()

# from orchestrator.tasks.server_metrics import craw_server_metrics

# Set the default Django settings module for the 'celery' program.

app = Celery('mesh')

app.conf.task_queues = (
    Queue('default', routing_key='default'),
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.task(name='craw_server_metrics')(craw_server_metrics)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
# app.conf.task_routes = {
#     'craw_server_metrics': {'queue': 'default'},
# }


