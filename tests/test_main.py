import os
import sys
from pathlib import Path

ROOT_DIR_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(os.path.join(ROOT_DIR_PATH))

from src import main as ez
from src import sub_ms2rss as sub


def test_001():
    # line通知テスト
    assert sub.send_line_notify("test!") == 200


def test_002():
    # ms2とexcelを起動するだけ。動作確認は目視でお願いします
    ez.open_workbook_with_ms2rss()


def test_003():
    # ms2とexcelを終了するだけ。動作確認は目視でお願いします
    ez.close_workbook_with_ms2rss()
