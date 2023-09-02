import logging
import os
import subprocess
from time import sleep

import pyautogui as py

logger = logging.getLogger(__name__)


# marcketspeed2開始
def start_ms2(ms2exeDir_path, USER_PASSWORD):
    global market_speed2
    current_dir = os.getcwd()
    os.chdir(os.path.expandvars(ms2exeDir_path))
    logging.debug("open MarketSpeed2.exe")
    market_speed2 = subprocess.Popen(
        os.path.expandvars(ms2exeDir_path + "/MarketSpeed2.exe")
    )
    logging.debug("sleep 15s. wait for updating of MarketSpeed2.exe")
    sleep(15)
    py.typewrite(USER_PASSWORD)
    py.keyDown("Enter")
    logging.debug("sleep 15s. wait for full activation of MarketSpeed2.exe")
    sleep(15)
    os.chdir(current_dir)


# ms2を停止する
def stop_ms2():
    logging.debug("kill the process of market_speed2")
    market_speed2.kill()


# ms2再起動（エクセルごといったほうがいいか？）
def restart_ms2(ms2exeDir_path, USER_PASSWORD):
    stop_ms2()
    start_ms2(ms2exeDir_path, USER_PASSWORD)
