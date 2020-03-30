import json

from os import getenv
from urllib.request import urlopen

space_id = getenv('CONTENTFUL_SPACE_ID')
contentful_base = f'https://cdn.contentful.com/spaces/{space_id}/environments/master'


def contentful_get_asset(resp_obj, asset_id):
    return next((
        'https:' + a['fields']['file']['url']
        for a in resp_obj['includes']['Asset']
        if a['sys']['id'] == asset_id
    ))


def get_sponsor_intro():
    return 'https://f1.srnd.org/sponsor-intro.mp3'


def get_sponsor_audio():
    access_token = getenv('CONTENTFUL_ACCESS_TOKEN')
    url = f'{contentful_base}/entries?content_type=globalSponsor&access_token={access_token}'
    with urlopen(url) as response:
        sponsor_info = json.loads(response.read())
        return [
            contentful_get_asset(
                sponsor_info, i['fields']['audio']['sys']['id'])
            for i in sponsor_info['items']
            if 'audio' in i['fields']
        ]
