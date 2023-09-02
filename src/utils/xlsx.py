import csv
import logging
import subprocess
from time import sleep

import numpy as np
import pandas as pd
import pyautogui as py
import xlwings as xw

logger = logging.getLogger(__name__)


def open_excel(excel_path, book_path, addin_path, order_trigger: bool):
    global xlsx_workbook
    global wb
    create_xlsx_book_for_margin_transaction(book_path)
    logging.debug("re-open transaction book on subprocess.")
    xlsx_workbook = subprocess.Popen([excel_path, book_path])
    logging.debug("sleep 10s, wait for full activation of workbook.")
    sleep(10)
    wb = xw.Book(book_path)
    wb.app.activate(steal_focus=True)
    logging.debug("load excel add-in.")
    rtn = wb.app.api.RegisterXLL(addin_path)
    logging.debug("load excel add-in has completed: %s", str(rtn))
    logging.debug("sleep 2s, wait for full activation of loading add-in.")
    sleep(2)
    kick_excel_addin(wb, order_trigger)
    initialize_xlsx_sheet_for_margin_transaction(wb)
    logging.debug("save xlsx book.")
    wb.save(book_path)
    logging.debug("sleep 2s, wait for saving xlsx.")
    sleep(2)


def close_excel():
    logging.debug("save book.")
    wb.save()
    logging.debug("sleep 2s, wait for saving xlsx.")
    sleep(2)
    logging.debug("close book.")
    wb.close()
    logging.debug("sleep 2s, wait for closing xlsx.")
    sleep(2)
    logging.debug("kill the process of xlsx_workbook.")
    kill_msg = xlsx_workbook.kill()
    logging.debug("kill command return here, %s", kill_msg)


# Add-in強制励起（ms2rss接続）
def kick_excel_addin(wb: xw.Book, order_trigger):
    # ==================================
    # step2．ステート確認してから適切な対処
    # xlwingsからvba呼び出し可能
    # https://resanaplaza.com/2021/08/29/%E3%80%90%E3%82%88%E3%81%8F%E5%88%86%E3%81%8B%E3%82%8B%E3%80%91xlwings-%E3%81%A7excel%E3%83%9E%E3%82%AF%E3%83%AD%E3%82%92%E5%AE%9F%E8%A1%8C%E3%81%97%E3%82%88%E3%81%86-by-python/
    # vbaからcommandBar状態確認？（コマンドIDがあるぽい。トグルに見えてIDは別ぽいので、ID特定できれば強制励起可能か？）
    # 接続状態か未接続状態か、発注可か発注不可かNameプロパティより状態を確認することはできる。
    # https://e-debugger.xyz/uiautomation%e3%81%a7excel%e3%82%92%e6%93%8d%e4%bd%9c%e3%81%99%e3%82%8b/
    # TODO：接続確認
    # TODO：強制励起
    # pyautogui.hotkey("alt", "5")  # ms2接続（エクセルでクイックアクセスツールバー左から5番目にms2接続を用意してある前提）
    # TODO：接続確認
    # TODO：注文可能ボタン状況確認
    # ==================================
    # step1．ステート無視して強制キック
    logging.debug("kick add-in button of connecting.")
    wb.app.activate(steal_focus=True)
    py.press("alt")
    sleep(0.1)
    py.press("y")
    py.press("2")
    sleep(0.1)
    py.press("y")
    py.press("1")
    logging.debug("sleep 5s, wait for button display to toggle.")
    sleep(5)
    if order_trigger:
        logging.debug("kick add-in button of order-enable.")
        wb.app.activate(steal_focus=True)
        py.press("alt")
        sleep(0.1)
        py.press("y")
        py.press("2")
        sleep(0.1)
        py.press("y")
        py.press("2")
        logging.debug("sleep 5s, wait for button display to toggle.")
        sleep(5)
    # ==================================
    return True


def duplicate_xlsx_to_csv(root_path):
    copy_xlsx_sheet_to_csv(root_path, "command")
    copy_xlsx_sheet_to_csv(root_path, "orderlist")
    copy_xlsx_sheet_to_csv(root_path, "orderidlist")
    copy_xlsx_sheet_to_csv(root_path, "positionlist")
    copy_xlsx_sheet_to_csv(root_path, "ticklist")


def copy_xlsx_sheet_to_csv(sink_root_path, sheet: str):
    valuelist = wb.sheets[sheet].used_range.options(ndim=2).value
    csv_path = sink_root_path + sheet + ".csv"
    logging.debug("copy xlsx sheet to txt >> %s.", sheet)
    f = open(csv_path, "w", newline="")
    writer = csv.writer(f)
    writer.writerows(valuelist)
    f.close()


def create_xlsx_book_from_duplicate_csv(root_path, dup_book_path):
    create_xlsx_book_for_margin_transaction(dup_book_path)
    logging.debug("open duplicated book.")
    wkbk = xw.Book(dup_book_path)
    wkbk.app.activate(steal_focus=True)
    copy_csv_to_xlsx_sheet(wkbk, root_path, "command")
    copy_csv_to_xlsx_sheet(wkbk, root_path, "orderlist")
    copy_csv_to_xlsx_sheet(wkbk, root_path, "orderidlist")
    copy_csv_to_xlsx_sheet(wkbk, root_path, "positionlist")
    copy_csv_to_xlsx_sheet(wkbk, root_path, "ticklist")
    # TODO: ↓これなんだ？
    # wkbk.save(book_path)
    logging.debug("sleep 2s, wait for saving xlsx.")
    sleep(2)
    logging.debug("close book.")
    wkbk.close()
    logging.debug("sleep 2s, wait for closing xlsx.")
    sleep(2)


def copy_csv_to_xlsx_sheet(wkbk: xw.Book, source_root_path, sheet: str):
    csv_path = source_root_path + sheet + ".csv"
    data = np.loadtxt(csv_path, delimiter=",", dtype="unicode")
    logging.debug("copy txt to xlsx sheet >> %s.", sheet)
    sht = wkbk.sheets[sheet]
    sht.activate()
    sleep(0.1)
    sht.range("A1").value = data
    sleep(0.1)


# 取引用workbook新規作成
def create_xlsx_book_for_margin_transaction(book_path):
    logging.debug("create new book.")
    wkbk = xw.Book()
    wkbk.save(book_path)
    sheet0 = wkbk.sheets[0]
    logging.debug("create new 5 sheets.")
    wkbk.sheets.add("command")
    wkbk.sheets.add("orderlist")
    wkbk.sheets.add("orderidlist")
    wkbk.sheets.add("positionlist")
    wkbk.sheets.add("ticklist")
    sleep(0.1)
    logging.debug("delete sheet: sheet1.")
    sheet0.delete()
    wkbk.save(book_path)
    logging.debug("sleep 2s, wait for saving xlsx.")
    sleep(2)
    logging.debug("close book.")
    wkbk.close()
    logging.debug("sleep 2s, wait for closing xlsx.")
    sleep(2)


# 取引用エクセルの各シート初期化処理
def initialize_xlsx_sheet_for_margin_transaction(wb: xw.Book):
    logging.debug("initialize sheet: command.")
    sht = wb.sheets["command"]
    sht.activate()
    ur = sht.used_range
    ur.clear_contents()
    sleep(0.1)
    logging.debug("initialize sheet: orderlist.")
    sht = wb.sheets["orderlist"]
    sht.activate()
    ur = sht.used_range
    ur.clear_contents()
    sleep(0.1)
    sht.range("A1").value = "=RssOrderList()"
    sleep(0.1)
    logging.debug("initialize sheet: orderidlist.")
    sht = wb.sheets["orderidlist"]
    sht.activate()
    ur = sht.used_range
    ur.clear_contents()
    sleep(0.1)
    sht.range("A1").value = "=RssOrderIDList()"
    sleep(0.1)
    logging.debug("initialize sheet: positionlist.")
    sht = wb.sheets["positionlist"]
    sht.activate()
    ur = sht.used_range
    ur.clear_contents()
    sleep(0.1)
    sht.range("A1").value = "=RssMarginPositionList()"
    sleep(0.1)
    logging.debug("initialize sheet: ticklist.")
    sht = wb.sheets["ticklist"]
    sht.activate()
    ur = sht.used_range
    ur.clear_contents()
    sleep(0.1)
    logging.debug("sleep 5s, wait for results to start updating.")
    sleep(5)


# 書込み対象のシートを指定してリストを流し込む。
def write_list_into_xlsxbook(book_path, sheet, commandlist):
    # このとき使用済み最下行の2つ下の行を起点とする
    wb = xw.Book(book_path)
    wb.app.activate(steal_focus=True)
    sht = wb.sheets[sheet]
    sht.activate()
    ur = sht.used_range
    logging.debug("write into xlsx book.")
    sht.range((ur.row + ur.rows.count, 1)).options(transpose=True).value = commandlist
    logging.info(
        "Here is recently executed query. \n %s",
        commandlist,
    )
    return True


# 読み込み対象のシートを指定してdfを返す
def read_matrix_from_xlsxbook(book_path, sheet):
    sht = xw.Book(book_path).sheets[sheet]
    sht.activate()
    ur = sht.used_range
    df = (
        sht.range(
            (2, 1),
            (
                # TODO: To be modified
                ur.row + ur.rows.count,
                # ur.column + ur.count,
                # 6007,
                50,
            ),
        )
        .options(pd.DataFrame, index=False, header=True, numbers=int)
        .value
    )
    if not df.empty:
        df = df.dropna(how="all", axis=1)
        df = df.replace("-", np.nan)
        df = df.replace("--------", np.nan)
        df = df.replace([None], np.nan)
        df = df.dropna(how="all", axis=0)
    return df
