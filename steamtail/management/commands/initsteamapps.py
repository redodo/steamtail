import requests
from django.db import transaction
from django.core.management.base import BaseCommand
from tqdm import tqdm

from steamtail.models import App


class Command(BaseCommand):
    help = 'Loads initial App IDs from Steam that are not in steamtail.'

    def handle(self, *args, **options):
        r = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        r.raise_for_status()
        data = r.json()

        with transaction.atomic():
            apps = tqdm(data['applist']['apps'])
            for app in apps:
                obj, created = App.objects.get_or_create(
                    id=app['appid'],
                    defaults=dict(
                        name=app['name'],
                    )
                )
                if created:
                    apps.set_description('Created %s' % obj.name)
