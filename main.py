import pandas as pd
from pathlib2 import Path
from twitter_crawler.core import util

chromedriver_path = Path('./driver/chromedriver').resolve()
destination = Path('/run/user/1000/gvfs/smb-share:server=192.168.2.11,share=smb/Documents/Dev/twitter-media').resolve()
headers_ = util.get_header(chromedriver_path, force=False, auth=False)
df = pd.DataFrame(util.scrape('Tesla', headers_, max_depth=1, following_scrape_limit=1000))
print(df)
df.to_csv("media.csv")
# util.sync_download(destination, df['url'].tolist())
failed_urls = util.multiprocess_download(destination, df['url'].tolist(), delay=1)
print(failed_urls)