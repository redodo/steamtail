import json

import pendulum
from celery import chord, shared_task
from django.db import transaction
from django.db.models import Q

import steamworker

from .models import App
from .utils import (
    init_apps,
    find_app_tags,
    update_app_tags,
)


@shared_task
def update_all_apps():
    init_apps()
    for app in App.objects.filter(Q(unknown=False) | Q(unknown=None)):
        update_app(app)


def update_app(app, refresh=True):
    # TODO: Implement refresh option.
    chord([
        steamworker.tasks.get_app_info.s(app.id),
        steamworker.tasks.get_store_page.s(app.id),
    ])(
        process_app_data.s(app.id)
    )


@shared_task
def process_app_data(data, app_id):
    app_info, store_page = data
    app = App.objects.get(id=app_id)

    if store_page is not None:
        if not isinstance(store_page, bytes):
            store_page = store_page.encode('utf-8')
        # Update tags
        tags = find_app_tags(store_page)
        update_app_tags(app, tags)

    app.unknown = app_info is None
    app.raw_info = app_info
    app.raw_store_page = store_page

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
    app.save()
