import re
import os
from typing import Dict, List, Set
import wget
import json
import tqdm
import time
import base64
import requests
import multiprocessing as mp
from seleniumwire import webdriver
from seleniumwire.utils import decode
from urllib.parse import unquote, quote
from .constant import DEFAULT_CHROME_OPTIONS
from pathlib2 import Path
from . import constant
from .profile import Profile


def get_headers(chromedriver_path: Path, options: List[str] = DEFAULT_CHROME_OPTIONS, force: bool = False):
    headers = None
    initialized = False

    def _get_headers():
        chrome_options = webdriver.ChromeOptions()
        for option in options:
            chrome_options.add_argument(option)
        if chromedriver_path:
            driver = webdriver.Chrome(chromedriver_path, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        driver.get(f'https://twitter.com')
        reqs = [req for req in driver.requests if re.match('https:\/\/twitter\.com.+Viewer\?variables.+', req.url)]
        req = reqs[0] if reqs else None
        return dict(req.headers) if req else None

    return headers if initialized and not force else _get_headers()


def get_header(chromedriver_path, options: List[str] = DEFAULT_CHROME_OPTIONS, force: bool = False, auth: bool = False):
    header_json = Path(os.getcwd()) / 'headers.json'
    if header_json.exists() and not force:
        with open(header_json, "r") as fr:
            headers = json.load(fr)
            return headers
    else:
        chrome_options = webdriver.ChromeOptions()
        for option in options:
            chrome_options.add_argument(option)
        driver = webdriver.Chrome(chromedriver_path, options=chrome_options)
        driver.get(f'https://twitter.com')
        if auth:
            input("Press Enter After login in")
        reqs = [req for req in driver.requests if re.match('https:\/\/twitter\.com.+Viewer\?variables.+', req.url)]
        req = reqs[-1] if reqs else None
        headers = dict(req.headers)
        with open(header_json, "w") as fw:
            json.dump(headers, fw, indent=2)
        return headers if req else None


def get_user_by_screen_name(username: str, headers: Dict):
    variables = {"screen_name": username, "withSafetyModeUserFields": True, "withSuperFollowsUserFields": True}
    variables_str = json.dumps(variables)
    url = constant.UserByScreenName_PREFIX + quote(variables_str)
    return requests.request("GET", url, headers=headers, data={})


def get_user_media_response(user_id: str, headers: Dict):
    variables = {
        "userId": user_id,
        "count": 10000,
        "includePromotedContent": False,
        "withSuperFollowsUserFields": True,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withSuperFollowsTweetFields": False,
        "withClientEventToken": False,
        "withBirdwatchNotes": False,
        "withVoice": False,
        "withV2Timeline": False,
        "__fs_interactive_text": False,
        "__fs_responsive_web_uc_gql_enabled": False,
        "__fs_dont_mention_me_view_api_enabled": False
    }
    variables_str = json.dumps(variables)
    url = constant.UserMedia_PREFIX + quote(variables_str)
    return requests.request("GET", url, headers=headers, data={})


def get_following_response(user_id: str, headers: Dict):
    variables = {
        "userId": user_id,
        "count": 10000,
        "includePromotedContent": False,
        "withSuperFollowsUserFields": True,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withSuperFollowsTweetFields": True,
        "__fs_interactive_text": False,
        "__fs_responsive_web_uc_gql_enabled": False,
        "__fs_dont_mention_me_view_api_enabled": False
    }
    variables_str = json.dumps(variables)
    url = constant.Following_PREFIX + quote(variables_str)
    return requests.request("GET", url, headers=headers, data={})


def extract_following_info(data: Dict):
    result = data['data']['user']['result']
    timeline = 'timeline_v2' if 'timeline_v2' in result.keys() else 'timeline'
    following_instruction = data["data"]["user"]["result"][timeline]["timeline"]["instructions"]
    following = list(filter(lambda obj: obj['type'] == 'TimelineAddEntries', following_instruction))[0]['entries']
    following_info = []
    for user in following:
        try:
            legacy = user['content']['itemContent']['user_results']['result']['legacy']
            following_info.append({
                "rest_id": user['content']['itemContent']['user_results']['result']['rest_id'],
                "name": legacy['name'],
                "media_count": legacy["media_count"],
                "created_at": legacy["created_at"],
                "description": legacy["description"],
                "followers_count": legacy["followers_count"],
                "normal_followers_count": legacy["normal_followers_count"],
                "screen_name": legacy["screen_name"]
            })
        except Exception as e:
            pass
    return following_info


def scrape(username: str, headers: Dict, depth: int = 0, max_depth: int = 1, following_scrape_limit: int = 5,
           scraped_screen_names: Set = set(), delay: float = 1.0):
    if depth > max_depth:
        return []
    print(f"{'  ' * depth}scrape {username}")
    if username in scraped_screen_names:
        print(f"skip {username}")
    scraped_screen_names.add(username)
    data = []
    profile = Profile(username, headers)
    try:
        urls = profile.get_user_media_urls()
        time.sleep(delay)
        following_info = profile.get_following_info()
    except Exception as e:
        print(e)
        print(f"Error: {username} failed")
        return []
    for url in urls:
        data.append({'username': username, 'url': url})
    if depth <= max_depth:
        for user in following_info[:following_scrape_limit]:
            data.extend(
                scrape(user['screen_name'], headers, depth + 1, max_depth, scraped_screen_names=scraped_screen_names,
                       following_scrape_limit=following_scrape_limit, delay=delay))
            time.sleep(delay)
    return data


def sync_download(destination: Path, urls: List[str], delay: float = 0.5):
    print("Downloading files")
    if not destination.exists():
        destination.mkdir(parents=True, exist_ok=True)
    for url in tqdm.tqdm(urls):
        try:
            wget.download(url, str(destination / url.split('/')[-1]))
            time.sleep(delay)
        except Exception as e:
            print(e)
            print(f"failed to download {url}")


def _download(data: Dict):
    try:
        target = data['destination'] / data['url'].split('/')[-1]
        if not target.exists():
            wget.download(data['url'], str(target))
        time.sleep(data['delay'])
    except Exception as e:
        return data['url']


def multiprocess_download(destination: Path, urls: List[str], delay: float = 0.5):
    to_download = [{"destination": destination, "url": url, "delay": delay} for url in urls]
    with mp.Pool(mp.cpu_count()) as p:
        failed_urls = list(tqdm.tqdm(p.imap(_download, to_download), total=len(to_download)))
    return list(filter(lambda url: url is not None, failed_urls))


def extract_user_id(data: Dict):
    return data['data']['user']['result']['rest_id']


def extract_profile_pic_url(data: Dict):
    return data['data']['user']['result']['legacy']['profile_image_url_https']


def extract_profile_banner_url(data: Dict):
    legacy = data['data']['user']['result']['legacy']
    if 'profile_banner_url' in legacy.keys():
        return legacy['profile_banner_url']
    else:
        return None


def extract_medias(data: Dict, entity_type: str = 'entities'):
    result = data['data']['user']['result']
    timeline = 'timeline_v2' if 'timeline_v2' in result.keys() else 'timeline'
    entries = result[timeline]['timeline']['instructions'][0]['entries']
    medias = []
    for entry in entries:
        if 'itemContent' in entry['content'].keys():
            result = entry['content']['itemContent']['tweet_results']['result']
            if 'legacy' in result.keys():
                entity = result['legacy'][entity_type]
                if 'media' in entity.keys():
                    medias.append(entity['media'])
    medias_flatten = [y for x in medias for y in x]
    return medias_flatten
