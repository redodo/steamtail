import os

from ._shared import *

CELERY_WORKER_CONCURRENCY = 1
CELERY_MAX_TASKS_PER_CHILD = 2

INSTALLED_APPS = [
    'steamworker',
]
