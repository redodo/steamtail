from django.core.management.base import BaseCommand

from steamtail.utils import init_apps


class Command(BaseCommand):
    help = 'Initializes new Steam apps'

    def handle(self, *args, **kwargs):
        init_apps()
