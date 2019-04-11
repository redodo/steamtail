from django.core.management.base import BaseCommand
from tqdm import tqdm
from neomodel import db

from steamgraph import models as graph
from steamtail import models


class Command(BaseCommand):
    help = 'Syncs the relational database with the graph database'

    def handle(self, *args, **options):
        with db.transaction:
            tags = {
                int(tag.id): graph.Tag(tag_id=tag.id, name=tag.name).save()
                for tag in tqdm(models.Tag.objects.all(), desc='Syncing tags')
            }
        with db.transaction:
            apps = {
                int(app.app_id): app
                for app in graph.App.create_or_update(*[
                    {'app_id': db_app.id, 'name': db_app.name}
                    for db_app in tqdm(models.App.objects.all(), desc='Syncing apps')
                ])
            }
        with db.transaction:
            users = {
                int(user.user_id): user
                for user in tqdm(graph.User.create_or_update(*[
                    {'user_id': db_user.id}
                    for db_user in models.User.objects.all()
                ]), desc='Syncing users')
            }

        with db.transaction:
            # Create AppTag relationships
            for app_tag in tqdm(models.AppTag.objects.all(), desc='Syncing app tags'):
                app = apps[app_tag.app_id]
                tag = tags[app_tag.tag_id]
                app.tags.connect(tag, {'votes': app_tag.votes})

        with db.transaction:
            # Create Friend relationships
            for db_user in tqdm(models.User.objects.prefetch_related('friends'), desc='Syncing friendships'):
                user = users[db_user.id]
                for db_friend in db_user.friends.all():
                    friend = users[db_friend.id]
                    user.friends.connect(friend)

        with db.transaction:
            # Create app ownership relations
            for user_app in tqdm(models.UserApp.objects.all(), desc='Syncing user apps'):
                user = users[user_app.user_id]
                app = apps[user_app.app_id]
                user.apps.connect(app, {'hours_played': user_app.hours_played})
