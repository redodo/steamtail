import json
import re

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings

from steamtail.decorators import kwarg_result


APP_LIST_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
APP_INFO_URL = 'https://store.steampowered.com/api/appdetails?appids={}'
STORE_PAGE_URL = 'https://store.steampowered.com/app/{}/'


@shared_task(rate_limit='40/m')
@kwarg_result(name='app_info')
def get_app_info(app_id):
    url = APP_INFO_URL.format(app_id)
    r = requests.get(url)

    # May raise a JSONDecodeError
    data = r.json()
    # May raise a KeyError
    data = data[str(app_id)]

    if data['success']:
        return data['data']
    else:
        # Normal response. The app is unknown.
        return None


@shared_task(rate_limit='40/m')
@kwarg_result(name='store_page')
def get_store_page(app_id, max_redirects=4):
    session = requests.session()
    session.max_redirects = max_redirects
    try:
        url = STORE_PAGE_URL.format(app_id)
        r = session.get(url)
        r.raise_for_status()
    except requests.TooManyRedirects:
        return None
    if '/app/' not in r.url:
        return None
    return r.text


def get_profile_games(user_id, html):
    raise NotImplementedError()


def get_profile_friends(user_id, html):
    soup = BeautifulSoup(html, 'lxml')
    return [el['data-steamid'] for el in soup.select('#friends_list [data-steamid]')]


GAMES = 1
FRIENDS = 2
PROFILE_SECTION_URLS = {
    GAMES:   'https://steamcommunity.com/profiles/[U:1:{}]/games/?tab=all',
    FRIENDS: 'https://steamcommunity.com/profiles/[U:1:{}]/friends',
}
PROFILE_SECTION_HANDLERS = {
    GAMES:   get_profile_games,
    FRIENDS: get_profile_friends,
}


@shared_task(rate_limit='60/m')
def get_profile_section(user_id, section):
    """Section redirects to the correct handling function. The reason those 
    functions aren't set up as different tasks is that we want to rate limit
    requests to the hostname.
    """
    url = PROFILE_SECTION_URLS[section].format(user_id)
    r = requests.get(url)
    r.raise_for_status()
    handler = PROFILE_SECTION_HANDLERS[section]
    return handler(user_id, r.text)
