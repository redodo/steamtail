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

    if settings.ENABLE_BINARY_TASK_RESULTS:
        return r.content
    else:
        return r.text
