from pathlib2 import Path
from twitter_crawler.core.session import Session
from twitter_crawler.core.profile import Profile
from twitter_crawler.core import util
from seleniumwire import webdriver
import re
import base64
from urllib.parse import unquote, quote
import pprint
import json
import requests
import time
from twitter_crawler.core.constant import DEFAULT_CHROME_OPTIONS
from typing import List, Dict
import os
import pandas as pd

chromedriver_path = Path('./driver/chromedriver').resolve()
destination = Path('./data').resolve()
headers_ = util.get_header(chromedriver_path, force=False, auth=False)

# headers = util.get_header(chromedriver_path, force=True, auth=True)
scraped_screen_names = set()

df = pd.DataFrame(util.scrape('sidking512', headers_))
print(df)
df.to_csv("media.csv")
util.sync_download(destination, df['url'].tolist())
