import requests


vanity_target = 'https://steamcommunity.com/profiles/{}/'


def get_vanity_url(user_id):
    r = requests.get(vanity_target.format(user_id), allow_redirects=False)
    r.raise_for_status()
    if 'location' in r.headers:
        return r.headers['location']
    return r.url
