import json
import re

from bs4 import BeautifulSoup
from django.db import transaction

from . import steam
from .models import App, AppTag, Tag


def init_apps():
    with transaction.atomic():
        apps = set(App.objects.values_list('id', flat=True))
        new_apps = []

        for app_id, name in steam.get_apps():
            if app_id not in apps:
                app = App(id=app_id, name=name)
                new_apps.append(app)

        App.objects.bulk_create(new_apps)


def update_app_tags(app, tags):
    # TODO: Optimize.
    with transaction.atomic():
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


app_tags_pattern = re.compile(r'\[{.*?"tagid".*?}\]')


def find_app_tags(soup):
    for script in soup.select('script:not([src])'):
        match = app_tags_pattern.search(script.text)
        if match:
            return json.loads(match.group())
    return []
