# import pytest
import os
import sys
from pathlib import Path

ROOT_DIR_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(os.path.join(ROOT_DIR_PATH))

from src import main as ez
from src import sub_ms2rss as sub


# line通知テスト
def t001():
    msg = "test!"
    sub.send_line_notify(msg)


# ms2とexcelを起動して終了するだけ
def t002():
    ez.open_workbook_with_ms2rss()
    ez.close_workbook_with_ms2rss()


if __name__ == "__main__":
    t001()
    t002()
