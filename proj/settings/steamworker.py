import os

from ._shared import *

CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

INSTALLED_APPS = [
    'steamworker',
]
