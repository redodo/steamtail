from django.core.management.base import BaseCommand
from django.db.models import Avg, Q, Variance
from tqdm import tqdm

from steamtail.models import App, User, UserApp


class Command(BaseCommand):
    help = 'Displays relevant apps to given apps.'

    def add_arguments(self, parser):
        parser.add_argument('app', type=int)

    def handle(self, *args, **options):
        app = App.objects.get(id=options['app'])

        print(':: Looking for suspected farmers...')
        farmers = UserApp.objects.values('user').annotate(
            hours_variance=Variance('hours_played'),
        ).filter(hours_variance__lte=10).values_list('user')
        print('== Filtered {} suspected farmers.'.format(len(farmers)))

        queryset = UserApp.objects.exclude(
            user__in=farmers,
        ).filter(
            app__type='game',
            hours_played__isnull=False,
        )

        print(':: Calculating average playtime for game...')
        app_average_playtime = queryset.filter(
            app=app,
            hours_played__isnull=False,
        ).aggregate(playtime=Avg('hours_played'))['playtime']
        print('== {:.2f} hours'.format(app_average_playtime))


        print(':: Calculating average playtime for all games...')
        average_playtimes = {
            result['app']: result['hours_played__avg']
            for result in
            queryset.values('app').annotate(Avg('hours_played'))
        }
        print('== Calculated average game playtime.')

        print(':: Selecting users that played this game...')
        players = {
            player.user_id: min(player.hours_played, app_average_playtime) / app_average_playtime
            for player in queryset.filter(app=app)
        }
        print('== {} players'.format(len(players)))


        print(':: Selecting records used for scoring...')
        other_playtimes = queryset.exclude(app=app).filter(user__in=players.keys())

        other_apps = {}

        iterator = tqdm(other_playtimes, desc='Play', total=other_playtimes.count())
        for play in iterator:
            if play.app not in other_apps:
                other_apps[play.app] = 0

            user_value = players[play.user_id]
            game_value = min(play.hours_played, average_playtimes[play.app_id]) / average_playtimes[play.app_id]

            other_apps[play.app] += user_value * game_value
