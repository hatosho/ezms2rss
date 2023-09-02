import logging
from datetime import datetime
from time import sleep

from tabulate import tabulate

from src import sub_ms2rss as ms2rss
from src.common.configs import configs
from src.common.logger import init_logger

init_logger(configs.LOGGER_CONFIG_PATH)
logger = logging.getLogger(__name__)


# ms2rss.xlsx開始
def open_workbook_with_ms2rss():
    try:
        # TODO：この時点でopenしているExcelはすべてkillする。
        # これ↑をやっておかないとms2の接続ができないとか変なポップアップが出ることあり
        logger.info("start >> open transaction-workbook.")
        ms2rss.start_excel_with_ms2rss()
        # TODO：監視プロセス開始
    except Exception as e:
        msg = "[異常検出終了] - ms2rss起動"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# ms2rss.xlsx終了
def close_workbook_with_ms2rss():
    try:
        # TODO：監視プロセス停止
        logger.info("close >> transaction-workbook.")
        ms2rss.stop_excel_with_ms2rss()
    except Exception as e:
        msg = "[異常検出終了] - ms2rss停止"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# 信用新規/返済注文->結果ステータス
def execute_order(orders: dict):
    try:
        if any(orders):
            querys = [""]
            orderid_prefix = ms2rss.m2u.calc_orderid_prefix()
            ord_get, ord_rls = ms2rss.m2u.classify_orders_into_get_or_release(orders)
            df_get = ms2rss.m2u.setup_input_dataframe_for_open(ord_get, orderid_prefix)
            querys_get = ms2rss.m2u.assemble_query_rssmarginpopenorder(df_get)
            querys.extend(querys_get)
            df_rls = ms2rss.m2u.setup_input_dataframe_for_close(ord_rls, orderid_prefix)
            querys_rls = ms2rss.m2u.assemble_query_rssmargincloseorder(df_rls)
            querys.extend(querys_rls)
            _ = ms2rss.m2u.set_order_querys_on_xlsx(querys)
            logger.debug("sleep 5s, wait for results to start updating.")
            sleep(5)
            status = ms2rss.m2u.get_ordernumbers_by_orderids(df_get, df_rls)
        else:
            status = {}
        return status
    except Exception as e:
        msg = "[異常検出続行] - 信用注文実行"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# キャンセル注文(construction)
# デイトレを前提とする。指定した銘柄についてすべての有効な注文をキャンセルする
# TODO:実装しなおし
# TODO:ステータスを返却
def execute_order_cancel(order_numbers: list):
    try:
        if order_numbers:
            # TODO：新規/返済に併せて構成を調整
            orderid_prefix = ms2rss.m2u.calc_orderid_prefix()
            _ = ms2rss.m2u.set_cancel_order_querys_on_xlsx(
                orderid_prefix, order_numbers
            )
            # TODO：キャンセルが成功したかどうかは拾っておきたい
            results_df = ms2rss.m2u.get_results_of_order_querys(
                orderid_prefix
            )  # ひとまず返却しておく
            print(results_df)
        else:
            pass
    except Exception as e:
        msg = "[異常検出続行] - 取消注文実行"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# 歩み値取得準備(construction)
def set_ticklist_board(stocks: list):
    try:
        ms2rss.set_tick_querys_on_xlsx(stocks)
        # TODO：更新が始まったことぐらい確認したい？
        return True
    except Exception as e:
        msg = "[異常検出続行] - 歩値取得準備"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# 現在値取得(construction)
def get_current_prices(dt: datetime, stocks: list):
    try:
        current_prices = ms2rss.get_currentprice_from_rssticklist(dt, stocks)
        return current_prices
    except Exception as e:
        msg = "[異常検出続行] - 現在値取得"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# 注文番号→注文履歴確認(construction)
def check_order_status(order_numbers: list):
    try:
        if order_numbers:
            order_status = ms2rss.m2u.search_rssorderlist_by_ordernumbers(order_numbers)
        else:
            order_status = {}
        return order_status
    except Exception as e:
        msg = "[異常検出続行] - 注文状況確認"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))


# 現在の建玉一覧取得
# TODO：指定した建玉のみ取得するよう改修
def get_margin_position_list(notification: bool):
    try:
        df = ms2rss.m2u.get_margin_position_list()
        msg = tabulate(df, showindex=False, headers="keys", tablefmt="simple")
        if notification:
            ms2rss.ln.send_line_notify(msg)
        logger.info(
            "current all holdings is below. \n %s",
            msg,
        )
        return df
    except Exception as e:
        msg = "[異常検出続行] - 建玉確認"
        logger.exception(msg)
        ms2rss.send_line_notify(msg + "\n[exception]" + str(e))
