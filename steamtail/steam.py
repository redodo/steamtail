import json
import re

import requests
from bs4 import BeautifulSoup


APP_LIST_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
APP_INFO_URL = 'https://store.steampowered.com/api/appdetails?appids={}'
STORE_PAGE_URL = 'https://store.steampowered.com/app/{}/'


def get_apps():
    r = requests.get(APP_LIST_URL)
    r.raise_for_status()
    data = r.json()
    for app in data['applist']['apps']:
        yield (int(app['appid']), app['name'])


def get_app_info(app_id):
    url = APP_INFO_URL.format(app_id)
    r = requests.get(url)

    # May raise a JSONDecodeError
    data = r.json()
    # May raise a KeyError
    data = data[str(app_id)]

    if data['success']:
        return data['data']

    # This is a normal response and should not be retried.
    return None


def get_store_page(app_id):
    session = requests.session()
    session.max_redirects = 5
    try:
        url = STORE_PAGE_URL.format(app_id)
        r = session.get(url)
        r.raise_for_status()
    except requests.TooManyRedirects:
        return b''
    if not r.url.startswith(url):
        return b''
    return r.content


app_tags_pattern = re.compile(r'\[{.*?"tagid".*?}\]')


def get_app_tags(app_id):
    store_page_html = get_store_page(app_id)
    soup = BeautifulSoup(store_page_html, 'lxml')

    for script in soup.select('script:not([src])'):
        match = app_tags_pattern.search(script.text)
        if match:
            return store_page_html, json.loads(match.group())
    return None, []
