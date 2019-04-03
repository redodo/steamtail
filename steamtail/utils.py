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
