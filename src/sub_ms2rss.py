import logging

# from datetime import datetime
from time import sleep

import numpy as np
import pandas as pd
import yaml
from tabulate import tabulate

from src import utils
from src.common.configs import configs

logger = logging.getLogger(__name__)

# 定義
pd.set_option("display.max_rows", 999)
pd.set_option("display.max_columns", 999)

with open(configs.CRED_CONFIG_PATH) as f:
    credentials = yaml.safe_load(f)
MS2_PASSWORD = credentials["RAKUTEN_SHOKEN"]["PASSWORD"]
LINE_TOKEN = credentials["LINE_NOTIFY"]["TOKEN"]
with open(configs.APP_CONFIG_PATH) as f:
    application = yaml.safe_load(f)
TMP_PATH = application["EZMS2RSS"]["LOCAL_TMP_ROOT_PATH"]
EXCEL_PATH = application["EXCEL"]["EXE_PATH"]
EXCEL_ADDIN_PATH = application["EXCEL"]["ADDIN_PATH"]
MS2_ROOT_PATH = application["RAKUTEN"]["MS2_ROOT_PATH"]
TRANSACTION_BOOK_PATH = TMP_PATH + "ms2rss_test.xlsx"
TRANSACTION_BOOK_ARCHIVE_PATH = TMP_PATH + "ms2rss_without_func.xlsx"

# 定数(必要か?外出しか?など調整中)
env_name = "dev"
EXEC_MODE = env_name
ORDER_TRRIGER = True if env_name == "prod" else False
# TODO：設定切り出し（0:特定口座, 1:一般口座）
bank_account_category = "0"


# line にメッセージ送信
def send_line_notify(message):
    EXEC_MODE = "prod"  # !!!!!!!!!!!!!test!!!!!!!!!!!!!
    utils.send_line_notify(EXEC_MODE, LINE_TOKEN, message)


# ms2起動 → excel起動
def start_excel_with_ms2rss():
    # py.hotkey("win", "m")
    utils.start_ms2(MS2_ROOT_PATH, MS2_PASSWORD)
    utils.open_excel(EXCEL_PATH, TRANSACTION_BOOK_PATH, EXCEL_ADDIN_PATH, ORDER_TRRIGER)


# ms2停止 → Excel閉じる
def stop_excel_with_ms2rss():
    # ひとまずcsvに複製して処理結果を残すようにする
    utils.duplicate_xlsx_to_csv(TMP_PATH)
    utils.stop_ms2()
    utils.close_excel()
    # TODO：csvをひとつのxlsxにまとめる
    # create_xlsx_book_from_duplicate_csv(
    #     TMP_PATH, self.dup_book_path
    # )


# 信用新規/返済注文実行
def set_order_querys_on_xlsx(querys: list):
    logger.debug("execute querys. >> rssmargin_xxx_order()")
    utils.write_list_into_xlsxbook(TRANSACTION_BOOK_PATH, "command", querys)


# キャンセル注文実行
def set_cancel_order_querys_on_xlsx(orderid_prefix: str, order_numbers: list):
    querys = utils.assemble_query_rsscancelorder(orderid_prefix, order_numbers)
    logger.debug("execute querys. >> rsscancelorder()")
    utils.write_list_into_xlsxbook(TRANSACTION_BOOK_PATH, "command", querys)


# !市況値取得準備(未使用)
def set_market_querys_on_xlsx(stocks: list):
    querys = utils.assemble_query_rssmarket(stocks)
    logger.debug("execute querys. >> rssmarket()")
    utils.write_list_into_xlsxbook(TRANSACTION_BOOK_PATH, "market", querys)
    logger.debug("sleep 2s, wait for results to start updating.")


# 歩み値取得準備
def set_tick_querys_on_xlsx(stocks: list):
    querys = utils.assemble_query_rssticklist(stocks)
    logger.debug("execute querys. >> rssticklist()")
    utils.write_list_into_xlsxbook(TRANSACTION_BOOK_PATH, "ticklist", querys)


# 注文実行状況確認（現場保存の意図でいったん残す）
# TODo：Excel毎回作り直しが実装できれば、これは不要。
def get_results_of_order_querys(orderid_prefix):
    logger.debug("sleep 5s, wait for results to start updating.")
    sleep(5)
    logger.debug("get query execution results.")
    df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "command")
    df = df.rename(columns={df.columns[0]: "history"})
    df = df.query("history.str.contains(@orderid_prefix)")
    logger.info(
        "query returns below. \n %s",
        tabulate(df, showindex=False, tablefmt="simple"),
    )
    return df


# !始値取得(未使用)
def get_openprice_from_rssmarket():
    df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "market")
    df = df.loc[:, ["銘柄コード", "現在日付", "始値詳細時刻", "始値"]]
    df = (df.astype({"銘柄コード": "int32"})).astype({"銘柄コード": "string"})
    df = df.astype({"始値": "int32"})
    return df


# 指定した時刻での現在値取得
# def get_currentprice_from_rssticklist(dt: datetime, stocks: list):
#     df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "ticklist")
#     df = df.loc[:, ["銘柄コード", "時刻", "出来高", "約定値"]]
#     # df = (df.astype({"銘柄コード": "int32"})).astype({"銘柄コード": "string"})
#     df = df.dropna(how="any")
#     df = df[df["銘柄コード"] != "銘柄コード"]
#     df = (df.astype({"銘柄コード": "int32"})).astype({"銘柄コード": "string"})
#     span_under, span_over = utils.calc_target_timespan(dt)
#     df_unique = df[["銘柄コード"]].drop_duplicates()
#     print(df_unique)
#     # TODO：to_datetime変換するときに日付が入っていないと自動で本日日付で埋められる。いずれ考えよう
#     df["時刻"] = pd.to_datetime(df["時刻"])
#     df = df[df["時刻"] < span_over]
#     df = df.loc[df.groupby("銘柄コード")["時刻"].idxmax(), :]
#     df["現在値"] = df["約定値"].where(df["時刻"] >= span_under)
#     df = df.set_index("銘柄コード")
#     logger.debug(
#         "current price detail is below, filterd by timestamp under %s and latest.\
#              \n %s",
#         dt,
#         tabulate(df, showindex=True, headers="keys", tablefmt="simple"),
#     )
#     dic = dict(zip(pd.Series(df.index, dtype=str), df["現在値"]))
#     stocks = map(str, stocks)
#     for stock in stocks:
#         if stock not in dic.keys():
#             dic[stock] = np.nan
#     return dic


# 建玉一覧取得
def get_margin_position_list():
    df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "positionlist")
    df = df.loc[:, ["銘柄コード", "銘柄名称", "建市場", "売買", "建日", "建値", "建玉数量"]]
    df = (df.astype({"銘柄コード": "int32"})).astype({"銘柄コード": "string"})
    df = (df.astype({"建日": "int32"})).astype({"建日": "string"})
    df = (df.astype({"建値": "int32"})).astype({"建値": "string"})
    df = df.astype({"建玉数量": "int32"})
    return df


# 注文番号s→注文状況一覧取(前提:最小単元株数での取引しかしない)
def search_rssorderlist_by_ordernumbers(order_numbers: list):
    ord_num_df = pd.DataFrame(order_numbers, columns=["注文番号"])
    ord_num_df = (ord_num_df.astype({"注文番号": "int32"})).astype({"注文番号": "string"})
    df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "orderlist")
    df = df.loc[:, ["注文番号", "通常注文状況", "銘柄コード", "売買"]]
    df = (df.astype({"注文番号": "int32"})).astype({"注文番号": "string"})
    df = (df.astype({"銘柄コード": "int32"})).astype({"銘柄コード": "string"})
    df = pd.merge(ord_num_df, df, on="注文番号", how="inner")
    if df.empty:
        raise ValueError("the specified order number does not exist.")
    df = utils.polish_dataframe_of_order_status(df)
    dic = df.set_index("brand").to_dict(orient="index")
    return dic


# 発注ID→注文番号&発注結果
def search_rssorderidlist_by_orderids(orderids: list):
    orderid_df = pd.DataFrame(orderids, columns=["発注ID"])
    orderid_df = (orderid_df.astype({"発注ID": "int32"})).astype({"発注ID": "string"})
    df = utils.read_matrix_from_xlsxbook(TRANSACTION_BOOK_PATH, "orderidlist")
    df = df.loc[:, ["発注ID", "注文番号", "発注結果"]]
    df = (df.astype({"発注ID": "int64"})).astype({"発注ID": "string"})
    df = df.fillna({"注文番号": 0})
    df = (df.astype({"注文番号": "int64"})).astype({"注文番号": "string"})
    df = df.rename(columns={"発注結果": "発注結果詳細"})
    df["発注結果"] = np.where(df["注文番号"] == 0, True, False)
    df = pd.merge(orderid_df, df, on="発注ID", how="inner")
    if df.empty:
        raise ValueError("the specified order number does not exist.")
    return df


# 発注IDから注文番号を検索して返す
# def get_ordernumbers_by_orderids(df_get, df_rls):
#     if not (df_get.empty or df_rls.empty):
#         df_get = df_get.loc[:, ["発注ID", "銘柄コード", "position"]]
#         df_rls = df_rls.loc[:, ["発注ID", "銘柄コード", "position"]]
#         orders = pd.concat([df_get, df_rls])
#     elif df_get.empty and df_rls.empty:
#         raise ValueError("the order does not exist.")
#     elif df_get.empty:
#         df_rls = df_rls.loc[:, ["発注ID", "銘柄コード", "position"]]
#         orders = df_rls
#     else:
#         df_get = df_get.loc[:, ["発注ID", "銘柄コード", "position"]]
#         orders = df_get
#     orderids = orders["発注ID"].to_list()
#     numbers = utils.search_rssorderidlist_by_orderids(orderids)
#     ord_join_num = pd.merge(orders, numbers, on="発注ID", how="left")
#     if ord_join_num.empty:
#         raise ValueError("the specified order number does not exist.")
#     # TODO：emptyだけでなくひとつでもnanが出たらエラー
#     ord_join_num = ord_join_num.rename(columns={"銘柄コード": "brand"})
#     ord_join_num = ord_join_num.rename(columns={"注文番号": "ordnum"})
#     ord_join_num = ord_join_num.loc[:, ["brand", "position", "ordnum"]]
#     dic = ord_join_num.set_index("brand").to_dict(orient="index")
#     return dic


# # 注文内容→注文番号(前提:最小単元株数での取引しかしない)
# def search_rssorderlist_by_orderdictionary(self, order_dic: dict):
#     return order_numbers
