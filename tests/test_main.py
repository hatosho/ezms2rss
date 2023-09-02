# import pytest
import os
import sys
from pathlib import Path

ROOT_DIR_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(os.path.join(ROOT_DIR_PATH))

from src import main as ez

env_name = ""
stocks = ["6563", "6564", "6565", "6566"]


# ms2とexcelを起動して終了するだけ
def t001():
    ez.open_workbook_with_ms2rss()
    ez.close_workbook_with_ms2rss()


if __name__ == "__main__":
    t001()
