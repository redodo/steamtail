from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Does some aggregation on tag votes.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            print('Updating total vote counts...')
            cursor.execute(
                "UPDATE steamtail_app a "
                "SET tag_votes = ("
                    "SELECT SUM(votes) FROM steamtail_apptag t "
                    "WHERE t.app_id = a.id"
                ")"
            )
            print('Updating tag shares...')
            cursor.execute(
                "UPDATE steamtail_apptag t "
                "SET share = CAST(votes AS FLOAT) / a.tag_votes "
                "FROM steamtail_app a "
                "WHERE a.id = t.app_id"
            )
