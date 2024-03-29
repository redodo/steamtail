import json
import re

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings

from steamtail.decorators import kwarg_result

from .utils import get_vanity_url


APP_LIST_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
APP_INFO_URL = 'https://store.steampowered.com/api/appdetails?appids={}'
STORE_PAGE_URL = 'https://store.steampowered.com/app/{}/'


@shared_task(bind=True, rate_limit='40/m')
@kwarg_result(name='app_info')
def get_app_info(self, app_id):
    url = APP_INFO_URL.format(app_id)
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response.status_code == 429 or exc.response.status_code >= 500:
            raise self.retry(exc=exc, countdown=60)
        else:
            raise

    # May raise a JSONDecodeError
    data = r.json()
    # May raise a KeyError
    data = data[str(app_id)]

    if data['success']:
        return data['data']
    else:
        # Normal response. The app is unknown.
        return None


@shared_task(bind=True, rate_limit='60/m')
@kwarg_result(name='store_page')
def get_store_page(self, app_id, max_redirects=2):
    session = requests.session()
    session.max_redirects = max_redirects
    try:
        url = STORE_PAGE_URL.format(app_id)
        r = session.get(url, cookies=dict(
            birthtime='0',
            lastagecheckage='1-0-1970',
            wants_mature_content='1',
        ))
        r.raise_for_status()
    except requests.TooManyRedirects:
        return None
    except requests.HTTPError as exc:
        if exc.response.status_code >= 500:
            # The server is having problems.
            raise self.retry(exc=exc, countdown=60)
        else:
            raise
    if '/app/' not in r.url:
        return None
    return r.text


games_pattern = re.compile(r'\[{.*?"appid".*?}\]')


PROFILE_FRIENDS_URL = 'https://steamcommunity.com/profiles/{}/friends'


@shared_task(bind=True, rate_limit='300/h')
def get_profile_games(self, user_id):
    url = '{}games/?tab=all'.format(get_vanity_url(user_id))
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response.status_code == 429:
            # Rate limit exceeded.
            raise self.retry(exc=exc, countdown=30)
        else:
            raise

    soup = BeautifulSoup(r.content, 'lxml')
    if soup.select_one('.profile_private_info'):
        return dict(
            data=[],
            is_public=False,
            is_ownership_public=False,
        )

    for script in soup.select('script:not([src])'):
        match = games_pattern.search(script.text)
        if match:
            data = json.loads(match.group())
            return dict(
                data=data,
                is_public=True,
                is_ownership_public=True,
            )

    return dict(
        data=[],
        is_public=True,
        is_ownership_public=False,
    )


def _is_friend_profile_private(friend_element):
    return (
        'offline' in friend_element['class'] and
        friend_element.select_one('.friend_last_online_text').text.strip().lower() == 'last online'
    )


@shared_task(rate_limit='100/m')
def get_profile_friends(user_id):
    url = PROFILE_FRIENDS_URL.format(user_id)
    r = requests.get(url)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, 'lxml')
    friends = []
    for friend in soup.select('#friends_list [data-steamid]'):
        is_public = not _is_friend_profile_private(friend)
        is_ownership_public = (
            # ownership is public when the user is in-game
            'in-game' in friend['class']
            # if the user is not in game, ownership should be private
            # when the profile is private
            or False if not is_public
            # we can not be certain, otherwise
            else None
        )

        friends.append((
            int(friend['data-steamid']),
            is_public,
            is_ownership_public,
        ))
    return friends
