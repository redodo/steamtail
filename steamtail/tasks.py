import json

import pendulum
from celery import shared_task
from django.db import transaction
from django.db.models import Q

from . import steam
from .models import App, AppTag, Tag
from .utils import init_apps, update_app_tags


@shared_task
def update_apps():
    with transaction.atomic():
        init_apps()
        for app in App.objects.filter(Q(unknown=False) | Q(unknown=None)):
            update_app.delay(app.id)


@shared_task(rate_limit='40/m')
def update_app(app_id, refresh=True):
    app = App.objects.get(id=app_id)

    if refresh or app.unknown is None:
        app_info = steam.get_app_info(app_id)
        update_app_tags(app)
    else:
        app_info = app.app_info

    app.unknown = app_info is None
    app.raw_info = app_info

    if app_info is not None:
        # Fields that are always in app_info
        app.type = app_info.get('type')
        app.name = app_info.get('name')
        app.short_description = app_info.get('short_description')
        app.is_free = app_info.get('is_free')

        # Optional fields
        if 'fullgame' in app_info and app_info['fullgame'].get('appid'):
            app.parent = App.objects.get(id=app_info['fullgame']['appid'])
        if 'release_date' in app_info:
            app.coming_soon = app_info.get('coming_soon', False)
            if app_info['release_date']['date']:
                try:
                    app.release_date = pendulum.parse(
                        app_info['release_date']['date'],
                        strict=False,
                    )
                except Exception as e:
                    e.args = (
                        '%s with release date %s' %
                        (e.args[0], app_info['release_date']['date']),
                    )
                    raise e

    app.save()

    return app_info
