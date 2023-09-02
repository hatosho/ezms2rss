import numpy as np


# 信用新規注文クエリ組立て
def assemble_query_rssmarginpopenorder(self, orders):
    querys = []
    for i, order in enumerate(orders.to_dict(orient="records")):
        query = (
            "=RssMarginOpenOrder("
            + str(order["発注ID"])
            + ","
            + str(order["発注トリガー"])
            + ","
            + str(order["銘柄コード"])
            + ","
            + str(order["売買区分"])
            + ","
            + str(order["注文区分"])
            + ","
            + str(order["SOR区分"])
            + ","
            + str(order["信用区分"])
            + ","
            + str(order["注文数量"])
            + ","
            + str(order["価格区分"])
            + ","
            + str(order["注文価格"])
            + ","
            + str(order["執行条件"])
            + ","
            + str(order["注文期限"])
            + ","
            + str(order["口座区分"])
            + ","
            + str(order["逆指値条件価格"])
            + ","
            + str(order["逆指値条件区分"])
            + ","
            + str(order["逆指値価格区分"])
            + ","
            + str(order["逆指値価格"])
            + ","
            + str(order["セット注文区分"])
            + ","
            + str(order["セット注文価格区分"])
            + ","
            + str(order["セット注文価格"])
            + ","
            + str(order["セット注文執行条件"])
            + ","
            + str(order["セット注文期限"])
            + ")"
        )
        querys.append(query)
    return querys


# 信用返済注文クエリ組立て
def assemble_query_rssmargincloseorder(self, orders):
    querys = []
    for i, order in enumerate(orders.to_dict(orient="records")):
        query = (
            "=RssMarginCloseOrder("
            + str(order["発注ID"])
            + ","
            + str(order["発注トリガー"])
            + ","
            + str(order["銘柄コード"])
            + ","
            + str(order["売買区分"])
            + ","
            + str(order["注文区分"])
            + ","
            + str(order["SOR区分"])
            + ","
            + str(order["信用区分"])
            + ","
            + str(order["注文数量"])
            + ","
            + str(order["価格区分"])
            + ","
            + str(order["注文価格"])
            + ","
            + str(order["執行条件"])
            + ","
            + str(order["注文期限"])
            + ","
            + str(order["口座区分"])
            + ","
            + str(order["建日"])
            + ","
            + str(order["建単価"])
            + ","
            + str(order["建市場"])
            + ","
            + str(order["逆指値条件価格"])
            + ","
            + str(order["逆指値条件区分"])
            + ","
            + str(order["逆指値価格区分"])
            + ","
            + str(order["逆指値価格"])
            + ")"
        )
        querys.append(query)
    return querys


# キャンセル注文クエリ組立て
def assemble_query_rsscancelorder(self, orderid_prefix, order_numbers):
    querys = [""]
    # TODO：新規/返済に合わせてリファクタ
    for i, order_number in enumerate(order_numbers):
        query = (
            "=RssCancelOrder("
            # "RssCancelOrder("
            + str(orderid_prefix + "3" + str(i))
            + ","
            + str(self.ORDER_TRRIGER)
            + ","
            + str(order_number)
            + ")"
        )
        querys.append(query)
    return querys


# 市況取得クエリ組立て
def assemble_query_rssmarket(self, stocks: list):
    querys = [["銘柄コード"], ["現在日付"], ["始値詳細時刻"], ["始値"], ["現在値詳細時刻"], ["現在値"]]
    for i, stock in enumerate(stocks):
        # TODO：np.arrayで書き直そう
        querys[0].append("=RssMarket(" + str(stock) + ',"銘柄コード")')
        querys[1].append("=RssMarket(" + str(stock) + ',"現在日付")')
        querys[2].append("=RssMarket(" + str(stock) + ',"始値詳細時刻")')
        querys[3].append("=RssMarket(" + str(stock) + ',"始値")')
        querys[4].append("=RssMarket(" + str(stock) + ',"現在値詳細時刻")')
        querys[5].append("=RssMarket(" + str(stock) + ',"現在値")')
    return querys


# 歩値取得クエリ組立て
def assemble_query_rssticklist(self, stocks: list):
    querys = np.array([[], [], [], [], []])
    row_interval = np.array([["--------", ""], ["", ""], ["", ""], ["", ""], ["", ""]])
    for i, stock in enumerate(stocks):
        row_num = str(i * 300 + 2)
        rss_query = (
            "=RssTickList("
            + "B"
            + row_num
            + ":D"
            + row_num
            + ',"'
            + str(stock)
            + '", 297)'
        )
        row_header = np.array([["銘柄コード"], ["時刻"], ["出来高"], ["約定値"], [rss_query]])
        querys = np.concatenate((querys, row_header), axis=1)
        for _ in range(297):
            row = np.array([[str(stock)], [""], [""], [""], [""]])
            querys = np.concatenate((querys, row), axis=1)
        querys = np.concatenate((querys, row_interval), axis=1)
    return querys
