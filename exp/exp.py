# %%
from urllib.parse import unquote, quote
import wget
import os
import tqdm
import json
import requests
import multiprocessing as mp
import shutil
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys

# %%
x = base64.b64decode("VXNlcjoxMzE4ODQzNjI0MDgwMTE3NzYx").decode('utf-8')
user_id = re.findall('\d+', x)[0]

# %%
url_prefix = "https://twitter.com/i/api/graphql/a7hxKT86vkxTe8TL1qLsNw/UserMedia?variables="
variables = {
    "userId": user_id,
    "count": 10000,
    "withTweetQuoteCount": False,
    "includePromotedContent": False,
    "withSuperFollowsUserFields": True,
    "withBirdwatchPivots": False,
    "withDownvotePerspective": False,
    "withReactionsMetadata": False,
    "withReactionsPerspective": False,
    "withSuperFollowsTweetFields": True,
    "withClientEventToken": False,
    "withBirdwatchNotes": False,
    "withVoice": True,
    "withV2Timeline": False,
    "__fs_dont_mention_me_view_api_enabled": False
}
variables_str = json.dumps(variables)
url = url_prefix + quote(variables_str)

# %%
payload = {}
headers = {
    'authority': 'twitter.com',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'x-twitter-client-language': 'en',
    'x-csrf-token': 'fa03a6b4522ea7ca4cf3b40ed1969073',
    'sec-ch-ua-mobile': '?0',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'x-guest-token': '1483459005225832461',
    'x-twitter-active-user': 'yes',
    'sec-ch-ua-platform': '"Linux"',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://twitter.com/xGbUtTRQHIA3gC6',
    'accept-language': 'en-CA,en;q=0.9',
    'cookie': 'guest_id_marketing=v1%3A164232250971935257; guest_id_ads=v1%3A164232250971935257; personalization_id="v1_0kRzJNfm+Uf7iL6RssmTbw=="; guest_id=v1%3A164232250971935257; ct0=c9b3e33dc61a5b0c5d7568aa9a322115; gt=1482634184296476674; _twitter_sess=BAh7BiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7AA%253D%253D--1164b91ac812d853b877e93ddb612b7471bebc74; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; guest_id=v1%3A164232313183552564; guest_id_ads=v1%3A164232313183552564; guest_id_marketing=v1%3A164232313183552564; personalization_id="v1_v7isx5phPZeznzSDlG6mzw=="'
}
response = requests.request("GET", url, headers=headers, data=payload)
data = response.json()
response.status_code

# %%


def get_medias(data, entity_type: str = 'entities'):
    entries = data['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
    medias = [entry['content']['itemContent']['tweet_results']['result']['legacy'][entity_type]['media']
              for entry in entries if 'itemContent' in entry['content'].keys()]
    medias_flatten = [y for x in medias for y in x]
    return medias_flatten


# %%
medias = get_medias(data)
urls = [media['media_url_https'] for media in medias]
media_url_set = set(urls)

# %%
if not os.path.exists('data'):
    os.mkdir('data')
for filepath in os.listdir('data'):
    os.remove(os.path.join('data', filepath))


def download(url):
    wget.download(url, os.path.join('data', url.split('/')[-1]))


for url in tqdm.tqdm(media_url_set):
    download(url)
print(mp.cpu_count())
# with mp.Pool(mp.cpu_count()) as p:
#     p.map(download, media_url_set)
# list(tqdm.tqdm(p.imap(download, media_url_set), total=len(media_url_set)))
