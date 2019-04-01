import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from steamtail.models import App


class Command(BaseCommand):
    help = 'Updates release dates.'
    date_formats = [
        '%d %b %Y', '%d %b, %Y',
        '%b %d %Y', '%b %d, %Y',
    ]

    def handle(self, *args, **options):
        with transaction.atomic():
            for app in tqdm(App.objects.filter(info__isnull=False, release_date=None)):
                data = json.loads(app.info)
                raw_date = data['release_date']['date'].strip()
                if not raw_date:
                    continue
                date = None
                for date_format in self.date_formats:
                    try:
                        date = datetime.strptime(
                            raw_date,
                            date_format,
                        )
                        break
                    except Exception as e:
                        continue
                app.release_date = date
                app.save()
