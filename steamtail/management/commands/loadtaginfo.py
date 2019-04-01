import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone

from steamtail.models import App, Tag
from steamtail.utils import Limiter


class Command(BaseCommand):
    help = 'Loads tag info from Steam.'
    url = 'http://store.steampowered.com/app/{}/'
    tag_selector = '#app_tagging_modal .app_tag_control'

    def handle(self, *args, **options):
        limiter = Limiter(1, 2, autosleep=False)

        apps = tqdm(App.objects.filter(info__isnull=False))
        for app in apps:
            apps.set_description(app.name)
            self.handle_app(app)

            sleep = limiter.limit()
            if sleep is not None:
                apps.set_description('...Sleeping...')
                time.sleep(sleep)

    def handle_app(self, app):
        url = self.url.format(app.id)
        r = requests.get(url)

        if not r.url.startswith(url):
            return

        app.store_page_html = r.content
        app.store_page_retrieved_on = timezone.now()
        app.save()
