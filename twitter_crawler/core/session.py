from .util import get_headers
from pathlib2 import Path
import os

class Session:
    def __init__(self, chromedriver_path: Path) -> None:
        self._chromedriver_path = chromedriver_path
        self.headers = get_headers(chromedriver_path, force=True)
        cwd = os.getcwd()

    def get_header(self):
        return self.headers
