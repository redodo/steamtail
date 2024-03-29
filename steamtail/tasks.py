import json
from decimal import Decimal

import pendulum
from bs4 import BeautifulSoup
from celery import chain, chord, shared_task
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

import steamworker.tasks

from .decorators import kwarg_inputs
from .models import App, User, UserApp
from .utils import (
    init_apps,
    find_app_tags,
    update_app_tags,
)


@shared_task
def update_all_apps():
    init_apps()
    for app in App.objects.exclude(unknown=True):
        update_app(app)


def update_app(app):
    chord([
        steamworker.tasks.get_app_info.s(app.id),
        steamworker.tasks.get_store_page.s(app.id),
    ])(
        process_app_data.s(app.id)
    )


@shared_task
@kwarg_inputs
def process_app_data(app_id, app_info, store_page):
    app = App.objects.get(id=app_id)

    if store_page is not None:
        store_page = store_page.encode('utf-8')
        soup = BeautifulSoup(store_page, 'lxml')

        # Update tags
        tags = find_app_tags(soup)
        update_app_tags(app, tags)

        # Update review counts
        try:
            app.positive_reviews = int(soup.select_one(
                'label[for=review_type_positive] .user_reviews_count'
            ).text.strip('()').replace(',', ''))
            app.negative_reviews = int(soup.select_one(
                'label[for=review_type_negative] .user_reviews_count'
            ).text.strip('()').replace(',', ''))
        except (AttributeError, ValueError):
            # there aren't any reviews
            pass

    app.unknown = app_info is None

    if app_info is not None:
        if app_info['steam_appid'] != app_id:
            # This app is likely redirecting to its parent app and
            # not giving accurate information. It is deleted to prevent
            # duplicate apps.
            app.delete()
            return

        # Fields that are always in app_info
        app.type = app_info.get('type')
        app.name = app_info.get('name')
        app.short_description = app_info.get('short_description')
        app.is_free = app_info.get('is_free')

        # Optional fields
        if 'fullgame' in app_info and app_info['fullgame'].get('appid'):
            try:
                app.parent = App.objects.get(id=app_info['fullgame']['appid'])
            except App.DoesNotExist:
                # TODO: Figure out a way to get the correct parent app in this case.
                pass
        if 'release_date' in app_info:
            app.coming_soon = app_info.get('coming_soon', False)
            if app_info['release_date']['date']:
                app.release_date_text = app_info['release_date']['date']
                try:
                    app.release_date = pendulum.parse(
                        app.release_date_text,
                        strict=False,
                    )
                except ValueError:
                    pass
    app.save()


DEFAULT_PROFILE_DELAY = 86400


def update_user_friends(user_id, max_depth=1, min_profile_delay=DEFAULT_PROFILE_DELAY):
    """
    :param min_profile_delay: the minimum delay between visits of the same profile
    """
    chain(
        steamworker.tasks.get_profile_friends.s(
            user_id,
        ),
        process_user_friends.s(
            user_id,
            max_depth=max_depth-1,
            min_profile_delay=min_profile_delay,
        ),
    ).delay()


@shared_task
def process_user_friends(friend_ids, user_id, max_depth=1, min_profile_delay=DEFAULT_PROFILE_DELAY):
    # efficiently create newly discovered users
    user_ids = friend_ids + [(
        user_id,
        len(friend_ids) != 0,
        None,
    )]
    users = {}
    for id, is_public, is_ownership_public in user_ids:
        defaults = {'is_public': is_public}
        if is_ownership_public is not None:
            defaults['is_ownership_public'] = is_ownership_public

        user, __ = User.objects.update_or_create(id=id, defaults=defaults)
        users[id] = user

    max_last_visited_on = (
        timezone.now() - timezone.timedelta(seconds=min_profile_delay)
    )

    # create connections between current user and friends
    user = users[user_id]

    for friend_id, is_public, __ in friend_ids:
        friend = users[friend_id]
        try:
            user.friends.add(friend)
        except IntegrityError:
            # The friendship is already registered
            # not really an issue when that fails.
            pass

        if is_public and max_depth != 0:
            if friend.friends_last_checked_on is None or \
                    friend.friends_last_checked_on < max_last_visited_on:
                # TODO: add refresh option
                # If max_depth has not been exceeded and the user
                # has friends. We can check if those profiles need
                # to be updated.
                update_user_friends(friend_id, max_depth=max_depth)

    user.friends_last_checked_on = timezone.now()
    user.save()


def update_user_apps(user_id):
    chain(
        steamworker.tasks.get_profile_games.s(user_id),
        process_user_apps.s(user_id),
    ).delay()


@shared_task
def process_user_apps(result, user_id):
    user, __ = User.objects.get_or_create(id=user_id)
    user.is_playtime_public = result.get(
        'is_ownership_public',
        user.is_playtime_public,
    )

    with transaction.atomic():
        for app_data in result['data']:
            app, __ = App.objects.get_or_create(
                id=app_data['appid'],
                defaults=dict(
                    name=app_data['name'],
                ),
            )

            hours_played = app_data.get('hours_forever')
            if hours_played:
                hours_played = Decimal(hours_played.replace(',', ''))
                user.is_playtime_public = True

            UserApp.objects.update_or_create(
                user=user,
                app=app,
                defaults=dict(
                    hours_played=hours_played,
                ),
            )

        user.is_public = result.get(
            'is_public',
            user.is_public,
        )
        user.is_ownership_public = result.get(
            'is_ownership_public',
            user.is_ownership_public,
        )
        user.apps_last_checked_on = timezone.now()
        user.save()
