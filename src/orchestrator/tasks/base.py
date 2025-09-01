from celery.app.task import Task
from celery.exceptions import TimeLimitExceeded
import logging
from decouple import config


class BaseTask(Task):
    # retry_kwargs = {'max_retries': 400, 'countdown': 1200}
    countdount = 60
    # autoretry_for = (Exception,)
    retry_jitter = True
    time_limit = 120
    wait_time_limit = 60
    # soft_time_limit = 30
    # acks_late = True
    retry_backoff = True
    max_retries = config("MAX_RETRIES", cast=int, default=5)
