from pathlib2 import Path
from twitter_crawler.core import util
import pandas as pd


destination = Path('./data').resolve()
urls = pd.read_csv("media.csv", index_col=0)['url'].tolist()
# util.sync_download(destination, urls)
failed_urls = util.multiprocess_download(destination, urls, delay=1)
print(failed_urls)
