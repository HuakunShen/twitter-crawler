import pandas as pd
from pathlib2 import Path
from twitter_crawler.core import util
import time

start = time.time()
chromedriver_path = Path('./driver/chromedriver').resolve()
destination = Path(
    '/run/user/1000/gvfs/smb-share:server=truenas.local,share=smb/Documents/Dev/twitter-media-3').resolve()
headers_ = util.get_header(chromedriver_path, force=False, auth=True)
df = pd.DataFrame(util.scrape('Anony99245444', headers_, max_depth=3, following_scrape_limit=1000))
print(df)
df.to_csv("media.csv")
# util.sync_download(destination, df['url'].tolist())
failed_urls = util.multiprocess_download(destination, df['url'].tolist(), delay=1)
print(failed_urls)

print(f"Time Taken: {time.time() - start}")
