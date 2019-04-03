from django.db import transaction

from . import steam
from .models import App


def init_apps():
    with transaction.atomic():
        apps = {
            app.id: app
            for app in App.objects.all()
        }
        new_apps = []

        for app_id, name in steam.get_apps():
            app = apps.get(app_id)
            if not app:
                app = App(id=app_id, name=name)
                new_apps.append(app)

        App.objects.bulk_create(new_apps)


def update_app_tags(app):
    raw_store_page, tags = steam.get_app_tags(app.id)
    for tag_info in tags:
        tag, __ = Tag.objects.get_or_create(
            id=tag_info['tagid'],
            defaults=dict(
                name=tag_info['name'],
            )
        )
        AppTag.objects.update_or_create(
            app=app,
            tag=tag,
            defaults=dict(
                votes=tag_info['count'],
                browseable=tag_info.get('browseable'),
            ),
        )
    app.raw_store_page = raw_store_page
    app.save()
