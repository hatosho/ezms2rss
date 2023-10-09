# import pytest
import os
import sys
from pathlib import Path

ROOT_DIR_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(os.path.join(ROOT_DIR_PATH))

from src import main as ez


# ms2‚Æexcel‚ğ‹N“®‚µ‚ÄI—¹‚·‚é‚¾‚¯
def t001():
    ez.open_workbook_with_ms2rss()
    ez.close_workbook_with_ms2rss()


if __name__ == "__main__":
    t001()
