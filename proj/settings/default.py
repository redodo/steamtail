import os
from ..utils import secret_from_env

from ._shared import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'admin_interface',
    'colorfield',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'steamtail',

    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

WSGI_APPLICATION = 'proj.wsgi.application'
ROOT_URLCONF = 'proj.urls'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
if 'USE_S3_STATICFILES' in os.environ:
    # Generic config for S3-like storages
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # DigitalOcean-specific config

    # TODO: make these configurable
    AWS_S3_REGION_NAME = 'ams3'
    AWS_STORAGE_BUCKET_NAME = 'steamtail'

    AWS_S3_ENDPOINT_URL = '${AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_ACCESS_KEY_ID = secret_from_env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = secret_from_env('AWS_SECRET_ACCESS_KEY')

    STATIC_URL = 'https://%s.%s/' % (
        AWS_STORAGE_BUCKET_NAME,
        AWS_S3_ENDPOINT_URL,
    )
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
