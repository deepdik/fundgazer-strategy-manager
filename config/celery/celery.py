import os

from celery import Celery


def make_celery():
    """
    """
    celery = Celery(
        'strategyManager',
    )
    celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "")
    celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "")
    celery.conf.include = ['api.utils.celery_tasks']
    celery.conf.task_create_missing_queues = True
    celery.conf.task_serializer = 'json'
    celery.conf.task_acks_late = True
    celery.conf.worker_prefetch_multiplier = 1
    return celery
