from datetime import datetime, timedelta, timezone

import pandas as pd


# under=前1分, over=前1秒
def calc_target_timespan(self, dt: datetime):
    span_over = dt + timedelta(minutes=1)
    span_under = dt
    return span_under, span_over


def calc_orderid_prefix(self):
    orderid_prefix = str(
        datetime.now(tz=timezone(timedelta(hours=9))).strftime("%H%M%S")
    )
    return orderid_prefix


def classify_orders_into_get_or_release(self, orders: dict):
    orders = pd.DataFrame(orders.values(), index=orders.keys())
    orders = orders.rename_axis("銘柄コード").reset_index()
    orders = orders.astype("Int64")
    orders = orders.astype({"銘柄コード": "string"})
    orders_get = self.initialize_dataframe_for_open(orders)
    orders_rls = self.initialize_dataframe_for_close(orders)
    return orders_get, orders_rls


def initialize_dataframe_for_open(self, orders):
    if (orders["position"] == 1).sum() > 0:
        orders_get = orders[orders["position"] == 1]
    else:
        orders_get = pd.DataFrame()
    return orders_get


def initialize_dataframe_for_close(self, orders):
    if (orders["position"] == 2).sum() > 0:
        orders_release = orders[orders["position"] == 2]
    else:
        orders_release = pd.DataFrame()
    return orders_release


# 新規注文の入力DF生成
def setup_input_dataframe_for_open(self, orders_get, orderid_prefix: str):
    if orders_get.empty:
        df_open = pd.DataFrame()
    else:
        df_open = orders_get.fillna(0)
        df_open = df_open.rename_axis("idx").reset_index()
        df_open = df_open.astype({"idx": "string"})
        df_open = df_open.assign(発注ID=orderid_prefix + "1" + df_open["idx"])
        df_open = df_open.assign(発注トリガー=self.ORDER_TRRIGER)
        # df_open = df_open.assign(銘柄コード)
        df_open = df_open.rename(columns={"action": "売買区分"})
        df_open = df_open.assign(注文区分="0")
        df_open = df_open.assign(SOR区分="0")
        df_open = df_open.assign(信用区分="4")
        df_open = df_open.rename(columns={"volume": "注文数量"})
        df_open = df_open.rename(columns={"category": "価格区分"})
        df_open = df_open.rename(columns={"price": "注文価格"})
        df_open = df_open.rename(columns={"option": "執行条件"})
        df_open = df_open.assign(注文期限="")
        df_open = df_open.assign(口座区分="0")
        df_open = df_open.assign(逆指値条件価格="")
        df_open = df_open.assign(逆指値条件区分="")
        df_open = df_open.assign(逆指値価格区分="")
        df_open = df_open.assign(逆指値価格="")
        df_open = df_open.assign(セット注文区分="0")
        df_open = df_open.assign(セット注文価格区分="")
        df_open = df_open.assign(セット注文価格="")
        df_open = df_open.assign(セット注文執行条件="")
        df_open = df_open.assign(セット注文期限="")
        df_open = (df_open.astype({"発注ID": "int32"})).astype({"発注ID": "string"})
        df_open = (df_open.astype({"売買区分": "int32"})).astype({"売買区分": "string"})
        df_open = (df_open.astype({"注文数量": "int32"})).astype({"注文数量": "string"})
        df_open = (df_open.astype({"価格区分": "int32"})).astype({"価格区分": "string"})
        df_open = (df_open.astype({"注文価格": "int32"})).astype({"注文価格": "string"})
        df_open = (df_open.astype({"執行条件": "int32"})).astype({"執行条件": "string"})
        df_open = df_open.replace({"注文価格": {"0": ""}})
    return df_open


# 返済注文の入力DF生成
def setup_input_dataframe_for_close(self, orders_rls, orderid_prefix: str):
    if orders_rls.empty:
        df_close = pd.DataFrame()
    else:
        holdings_all = self.get_margin_position_list()
        df_close = self.filter_holdings_by_orders(holdings_all, orders_rls)
        df_close = df_close.fillna(0)
        df_close = df_close.rename_axis("idx").reset_index()
        df_close = df_close.astype({"idx": "string"})
        df_close = df_close.assign(発注ID=orderid_prefix + "2" + df_close["idx"])
        df_close = df_close.assign(発注トリガー=self.ORDER_TRRIGER)
        # df_close = df_close.assign(銘柄コード)
        df_close = df_close.rename(columns={"action": "売買区分"})
        df_close = df_close.assign(注文区分="0")
        df_close = df_close.assign(SOR区分="0")
        df_close = df_close.assign(信用区分="4")
        df_close = df_close.rename(columns={"volume": "注文数量"})
        df_close = df_close.rename(columns={"category": "価格区分"})
        df_close = df_close.rename(columns={"price": "注文価格"})
        df_close = df_close.rename(columns={"option": "執行条件"})
        df_close = df_close.assign(注文期限="")
        df_close = df_close.assign(口座区分="0")
        # df_close = df_close.assign(建日)
        df_close = df_close.rename(columns={"建値": "建単価"})
        df_close = df_close.replace({"建市場": {"東証": "1", "JNX": "4", "Chi-X": "6"}})
        df_close = df_close.assign(逆指値条件価格="")
        df_close = df_close.assign(逆指値条件区分="")
        df_close = df_close.assign(逆指値価格区分="")
        df_close = df_close.assign(逆指値価格="")
        df_close = (df_close.astype({"発注ID": "int32"})).astype({"発注ID": "string"})
        df_close = (df_close.astype({"売買区分": "int32"})).astype({"売買区分": "string"})
        df_close = (df_close.astype({"注文数量": "int32"})).astype({"注文数量": "string"})
        df_close = (df_close.astype({"価格区分": "int32"})).astype({"価格区分": "string"})
        df_close = (df_close.astype({"注文価格": "int32"})).astype({"注文価格": "string"})
        df_close = (df_close.astype({"執行条件": "int32"})).astype({"執行条件": "string"})
        df_close = df_close.replace({"注文価格": {"0": ""}})
    return df_close


def filter_holdings_by_orders(self, holdings_all, orders_rls):
    holdings = pd.merge(
        orders_rls,
        holdings_all,
        on="銘柄コード",
        how="inner",
    )
    # TODO：filterした結果 emptyの辞書が返ったらエラー
    if holdings.empty:
        raise ValueError("the specified order number does not exist.")
    # TODO：指定した建玉が含まれていなければエラー
    # TODO：存在するが数量×売買区分が想定通りでなければエラー
    return holdings


def polish_dataframe_of_order_status(self, order_status_df):
    # TODO：joinしなくてreplaceで書き直せる
    # TODO：関数名はsetup_inputに寄せられるか？
    status_chart = pd.DataFrame(
        data=[[1, "約定"], [2, "執行中"]],
        columns=["status", "通常注文状況"],
    )
    position_chart = pd.DataFrame(
        data=[[1, "買建"], [1, "売建"], [2, "買埋"], [2, "売埋"]],
        columns=["position", "売買"],
    )
    order_status_df = pd.merge(
        order_status_df,
        status_chart,
        on="通常注文状況",
        how="left",
    )
    order_status_df = pd.merge(
        order_status_df,
        position_chart,
        on="売買",
        how="left",
    )
    order_status_df = order_status_df.fillna({"status": 3})
    order_status_df = order_status_df.rename(columns={"銘柄コード": "brand"})
    order_status_df = order_status_df.loc[:, ["brand", "position", "status"]]
    order_status_df = (order_status_df.astype({"brand": "int32"})).astype(
        {"brand": "string"}
    )
    order_status_df = order_status_df.astype({"status": "int32"})
    order_status_df = order_status_df.astype({"position": "int32"})
    return order_status_df
