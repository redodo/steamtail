import json
import time

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from steamtail.models import App
from steamtail.utils import Limiter


class Command(BaseCommand):
    help = 'Loads app info from Steam.'
    url = 'http://store.steampowered.com/api/appdetails?appids={}'

    def handle(self, *args, **options):
        limiter = Limiter(15, 24, autosleep=False)

        apps = tqdm(App.objects.filter(info=None))
        for app in apps:
            apps.set_description(app.name)
            self.handle_app(app)

            sleep = limiter.limit()
            if sleep is not None:
                apps.set_description('...Sleeping...')
                time.sleep(sleep)

    def handle_app(self, app):
        r = requests.get(self.url.format(app.id))
        data = r.json()
        if data is None:
            return
        data = data[str(app.id)]
        if 'data' not in data:
            return
        data = data['data']

        if 'dlc' in data:
            App.objects.filter(id__in=data['dlc']).update(parent=app)

        app.info = json.dumps(data).encode('utf-8')
        app.name = data['name']
        app.type = data['type']
        app.save()
