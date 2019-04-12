from decimal import Decimal

from django.db.models import Avg, Q, Func, F, Variance, Sum, Value, FloatField
from django.db.models.functions import Cast
from django.views.generic import DetailView
from django.shortcuts import render

from .models import App, AppTag, UserApp


def apps_like_this(request, pk_a):
    app = App.objects.get(id=pk_a)


    similar_apps = App.objects.raw("""
SELECT
a2.app_id as id,
sum(
abs(a2.share - coalesce(
    (select
    CAST(a.votes AS FLOAT) / (select sum(votes) from steamtail_apptag where app_id = a.app_id)
    from steamtail_apptag a
    where app_id = %s and tag_id=a2.tag_id), 0
))
) as diff
from (
    select
    a1.app_id,
    a1.tag_id,
    (select sum(votes) from steamtail_apptag where app_id = a1.app_id) as total,
    CAST(votes AS FLOAT) / (select sum(votes) from steamtail_apptag where app_id = a1.app_id) as share
    from steamtail_apptag a1
) as a2
inner join steamtail_app A on a2.app_id = A.id
where a2.app_id != %s
and A.type = 'game'
and a2.total >= 20
group by a2.app_id
order by diff
limit 69
    """, [app.id, app.id])

    return render(request, 'steamtail/app_relevant.html', dict(
        app=app,
        similar_apps=similar_apps,
    ))


def app_similarity(request, pk_a, pk_b):
    app_tags = AppTag.objects.exclude(tag_id__in=[
        113,   # Free to Play
        492,   # Indie
        1756,  # Great Soundtrack
    ])

    a = App.objects.get(pk=pk_a)
    b = App.objects.get(pk=pk_b)

    a_votes = app_tags.filter(app=a).aggregate(Sum('votes'))['votes__sum']
    a_tags = app_tags.filter(app=a).annotate(
        share=Cast('votes', FloatField()) / Value(a_votes) * Value(100),
    ).order_by('-votes')

    b_votes = app_tags.filter(app=b).aggregate(Sum('votes'))['votes__sum']
    b_tags = app_tags.filter(app=b).annotate(
        share=Cast('votes', FloatField()) / Value(b_votes) * Value(100),
    ).order_by('-votes')

    table = {}
    for a_tag in a_tags:
        table[a_tag.tag] = dict(
            a_votes=a_tag.votes,
            a_share=a_tag.share,
            b_votes=0,
            b_share=0,
            diff=a_tag.share,
        )
    for b_tag in b_tags:
        if b_tag.tag not in table:
            table[b_tag.tag] = dict(
                a_votes=0,
                a_share=0,
            )
        table[b_tag.tag].update(
            b_votes=b_tag.votes,
            b_share=b_tag.share,
            diff=abs(b_tag.share - table[b_tag.tag]['a_share']),
        )

    diff = sum(
        row['diff']
        for row in table.values()
    )
    similarity = abs((1 - diff / 200) * 100)

    for key, value in table.items():
        value.update(tag=key)
    table = table.values()
    print(table)

    return render(request, 'steamtail/app_similarity.html', dict(
        a=a,
        b=b,
        a_votes=a_votes,
        b_votes=b_votes,
        table=table,
        diff=diff,
        similarity=similarity,
    ))


class AppInfo(DetailView):
    model = App
    template_name = 'steamtail/app_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_info'] = self.get_tag_info(self.object)
        if self.kwargs.get('other'):
            other = App.objects.get(id=self.kwargs.get('other'))
            context['other'] = other
            context['other_tag_info'] = self.get_tag_info(other)
        return context

    def get_tag_info(self, app):
        app_tags = AppTag.objects.exclude(tag_id__in=[
            492,   # Indie
            1756,  # Great Soundtrack
        ])

        votes = app_tags.filter(app=app).aggregate(Sum('votes'))['votes__sum']
        tags = app_tags.filter(app=app).annotate(
            share=Cast('votes', FloatField()) / Value(votes) * Value(100),
        ).order_by('-votes')
        return tags, votes


class AppDetail(DetailView):
    model = App

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.operations = 0
        context['relevant_apps'] = list(self.get_relevant_apps())
        context['operations'] = self.operations
        return context

    def get_relevant_apps(self):
        boosters = UserApp.objects.filter(
            hours_played__gte=10000,
        ).distinct('user').values_list('user')
        print(':: Filtered {} suspected boosters.'.format(len(boosters)))

        farmers = UserApp.objects.values('user').annotate(
            hours_variance=Variance('hours_played'),
        ).filter(hours_variance__lte=10).values_list('user')
        print(':: Filtered {} suspected farmers.'.format(len(farmers)))

        excluded_users = set(boosters) | set(farmers)

        user_apps = UserApp.objects.exclude(
            user__in=excluded_users,
        ).filter(
            app__type='game',
        )

        app = self.object
        apps = {}  # app: score
        average_playtimes = {} # app: average_playtime

        # get average playtime
        average_played = user_apps.filter(
            app=app,
            hours_played__isnull=False,
        ).aggregate(Avg('hours_played'))['hours_played__avg']

        # select users that have played this app for atleast 5% of the average playtime
        users = user_apps.filter(
            app=app,
            hours_played__gte=average_played * Decimal(0.05),
        ).order_by('hours_played')[::40]

        print('Max lookups: {}'.format(len(users) * 20))

        for user in users:
            user_importance = min(user.hours_played, average_played) / average_played

            # get other app the user has played
            for other_app in user_apps.filter(
                        ~Q(app=app),
                        user=user.user,
                        hours_played__isnull=False,
                    ).order_by('-hours_played')[:40]:
                if other_app.app not in apps:
                    apps[other_app.app] = 0
                    average_playtimes[other_app.app] = user_apps.filter(
                        app=other_app.app,
                        hours_played__isnull=False,
                    ).aggregate(Avg('hours_played'))['hours_played__avg']

                other_app_average_played = average_playtimes[other_app.app]
                other_app_importance = (
                    min(other_app.hours_played, other_app_average_played) /
                    other_app_average_played
                )

                self.operations += 1
                apps[other_app.app] += other_app_importance * user_importance

        print('starting context preparation')

        apps = sorted(apps.items(), key=lambda i: i[1], reverse=True)[:39]
        for app, relevance in apps:
            yield app, relevance, app.tags.all()[:5], average_playtimes[app]
