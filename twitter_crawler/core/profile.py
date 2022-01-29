import pprint
from typing import List
from . import util


class Profile:
    def __init__(self, username: str, headers: dict) -> None:
        self.headers = headers
        self.username = username
        user_by_screen_name_res = util.get_user_by_screen_name(username, self.headers)
        user_by_screen_name_data = user_by_screen_name_res.json()
        self.user_id = util.extract_user_id(user_by_screen_name_data)
        self.profile_pic_url = util.extract_profile_pic_url(user_by_screen_name_data)
        self.profile_banner_url = util.extract_profile_banner_url(user_by_screen_name_data)
        self.medias = None
        self.following_info = None

    def get_user_medias(self):
        """
        format of a media object
        [{
            'display_url': 'pic.twitter.com/lIcDY8BPJB',
            'expanded_url': 'https://twitter.com/Tesla/status/1487181448490766347/photo/1',
            'id_str': '1487181442169847808',
            'indices': [96, 119],
            'media_url_https': 'https://pbs.twimg.com/media/FKOHpGkWQAA1QBe.jpg',
            'type': 'photo',
            'url': 'https://t.co/lIcDY8BPJB',
            'features': {'large': {'faces': []},
                            'medium': {'faces': []},
                            'small': {'faces': []},
                            'orig': {'faces': []}},
            'sizes':
            {'large': {'h': 1024, 'w': 2048, 'resize': 'fit'},
                'medium': {'h': 600, 'w': 1200, 'resize': 'fit'},
                'small': {'h': 340, 'w': 680, 'resize': 'fit'},
                'thumb': {'h': 150, 'w': 150, 'resize': 'crop'}},
            'original_info':
            {'height': 1024, 'width': 2048,
                'focus_rects':
                [{'x': 110, 'y': 0, 'w': 1829, 'h': 1024},
                {'x': 512, 'y': 0, 'w': 1024, 'h': 1024},
                {'x': 575, 'y': 0, 'w': 898, 'h': 1024},
                {'x': 768, 'y': 0, 'w': 512, 'h': 1024},
                {'x': 0, 'y': 0, 'w': 2048, 'h': 1024}]}
        }]

        Returns:
            List[Dict]: [description]
        """
        if self.medias is None:
            user_media_response = util.get_user_media_response(self.user_id, self.headers)
            self.medias = util.extract_medias(user_media_response.json())
        return self.medias

    def get_user_media_urls(self):
        return [media['media_url_https'] for media in self.get_user_medias()]

    def get_user_media_tweets_urls(self):
        return [media['url'] for media in self.get_user_medias()]

    def get_following_info(self) -> List:
        if self.following_info is not None:
            return self.following_info
        res = util.get_following_response(self.user_id, self.headers)
        if res.status_code != 200:
            return None
        else:
            self.following_info = util.extract_following_info(res.json())
            return self.following_info
