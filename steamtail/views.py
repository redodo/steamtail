from decimal import Decimal

from django.db.models import Avg, Q
from django.views.generic import DetailView

from .models import App, UserApp


class AppDetail(DetailView):
    model = App

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relevant_apps'] = self.get_relevant_apps()
        return context

    def get_relevant_apps(self):
        app = self.object
        apps = {}  # app: score
        average_playtimes = {} # app: average_playtime

        # get average playtime
        average_played = UserApp.objects.filter(
            app=app,
            hours_played__isnull=False,
        ).aggregate(Avg('hours_played'))['hours_played__avg']
        print(average_played)

        # select users that have played this app for atleast 5% of the average playtime
        users = UserApp.objects.filter(app=app, hours_played__gte=1)

        for user in users:
            user_importance = min(user.hours_played, average_played) / average_played

            # get other app the user has played
            for other_app in UserApp.objects.filter(
                        ~Q(app=app),
                        user=user.user,
                        hours_played__gte=10,
                    ):
                if other_app.app not in apps:
                    apps[other_app.app] = 0
                    average_playtimes[other_app.app] = UserApp.objects.filter(
                        app=other_app.app,
                        hours_played__isnull=False,
                    ).aggregate(Avg('hours_played'))['hours_played__avg']

                other_app_average_played = average_playtimes[other_app.app]
                other_app_importance = (
                    min(other_app.hours_played, other_app_average_played) /
                    other_app_average_played
                )

                apps[other_app.app] += other_app_importance * user_importance

        apps = sorted(apps.items(), key=lambda i: i[1], reverse=True)[:39]
        for app, relevance in apps:
            yield app, relevance, app.tags.all()[:5]
