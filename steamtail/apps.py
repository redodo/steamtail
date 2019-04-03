from django.apps import AppConfig


class SteamtailConfig(AppConfig):
    name = 'steamtail'

    def ready(self):
        from .utils import init_apps
        init_apps()
