import json

import pendulum
from celery import chain, chord, shared_task
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

import steamworker.tasks

from .decorators import kwarg_inputs
from .models import App, User
from .utils import (
    init_apps,
    find_app_tags,
    update_app_tags,
)


@shared_task
def update_all_apps():
    init_apps()
    for app in App.objects.filter(Q(unknown=False) | Q(unknown=None)):
        update_app(app)


def update_app(app, refresh=True):
    chord_tasks = []
    if refresh or app.raw_info is None:
        chord_tasks.append(
            steamworker.tasks.get_app_info.s(app.id)
        )
    if refresh or app.raw_store_page is None:
        chord_tasks.append(
            steamworker.tasks.get_store_page.s(app.id)
        )
    process_app_data_task = process_app_data.s(app.id)
    if chord_tasks:
        chord(chord_tasks)(process_app_data_task)
    else:
        process_app_data_task.delay()


@shared_task
@kwarg_inputs
def process_app_data(app_id, app_info=None, store_page=None):
    app = App.objects.get(id=app_id)
    app_info = app_info or app.raw_info
    store_page = store_page or app.raw_store_page

    if store_page is not None:
        store_page = store_page.encode('utf-8')
        # Update tags
        tags = find_app_tags(store_page)
        update_app_tags(app, tags)

    app.unknown = app_info is None
    app.raw_info = app_info
    app.raw_store_page = store_page

    if app_info is not None:
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
                try:
                    app.release_date = pendulum.parse(
                        app_info['release_date']['date'],
                        strict=False,
                    )
                except Exception as e:
                    e.args = (
                        '%s with release date %s' %
                        (e.args[0], app_info['release_date']['date']),
                    )
    app.save()


DEFAULT_PROFILE_DELAY = 86400


def update_user_friends(user_id, max_depth=1, min_profile_delay=DEFAULT_PROFILE_DELAY):
    """
    :param min_profile_delay: the minimum delay between visits of the same profile
    """
    chain(
        steamworker.tasks.get_profile_section.s(
            user_id,
            section=steamworker.tasks.FRIENDS,
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
    user_ids = friend_ids + [(user_id, None)]
    users = {
        user.id: user
        for user in User.objects.filter(id__in=[u[0] for u in user_ids])
    }
    new_users = []
    for id, is_private in user_ids:
        if id not in users:
            new_user = User(id=id, is_private=is_private)
            new_users.append(new_user)
            users[id] = new_user
    User.objects.bulk_create(new_users)

    max_last_visited_on = (
        timezone.now() - timezone.timedelta(seconds=min_profile_delay)
    )

    # create connections between current user and friends
    with transaction.atomic():
        user = users[user_id]

        for friend_id, is_private in friend_ids:
            friend = users[friend_id]
            user.friends.add(friend)

            if not is_private and max_depth != 0:
                if friend.last_visited_on is None or \
                        friend.last_visited_on < max_last_visited_on:
                    # TODO: add refresh option
                    # If max_depth has not been exceeded and the user
                    # has friends. We can check if those profiles need
                    # to be updated.
                    update_user_friends(friend_id, max_depth=max_depth)

        user.last_visited_on = timezone.now()
        user.save()
