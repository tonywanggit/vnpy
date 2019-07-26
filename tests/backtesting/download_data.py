# -*- coding: utf-8 -*-
# @Time    : 2019/7/22 9:33
# @Author  : Tony
"""下载数据"""
from datetime import datetime
from numpy import size

from trader.constant import Interval, Exchange
from trader.database import database_manager
from trader.object import HistoryRequest
from trader.rqdata import rqdata_client


def download_history_data(symbol, exchange):
    print(symbol, exchange)
    begin_date = datetime.strptime("2018-01-01", "%Y-%m-%d")

    for i in range(2):
        start_date = begin_date.replace(year=begin_date.year + i)
        end_date = begin_date.replace(year=begin_date.year + i + 1)

        print(start_date, end_date)
        req = HistoryRequest(
            symbol=symbol,
            exchange=Exchange(exchange),
            interval=Interval("1m"),
            start=start_date,
            end=end_date
        )
        data = rqdata_client.query_history(req)
        print(size(data))
        database_manager.save_bar_data(data)


if __name__ == '__main__':
    rqdata_client.init()

    # 实盘品种
    # download_history_data("RB1910", "SHFE")   # 螺纹钢
    # download_history_data("AL1910", "SHFE")   # 沪铝
    # download_history_data("CU1910", "SHFE")   # 铜
    # download_history_data("ZN1910", "SHFE")   # 锌

    # download_history_data("C911", "DCE")     # 玉米
    # download_history_data("JD1911", "DCE")    # 鲜鸡蛋
    # download_history_data("I1911", "DCE")     # 铁矿石
    # download_history_data("J1911", "DCE")     # 冶金焦炭
    # download_history_data("M1911", "DCE")     # 豆粕

    # download_history_data("PM911", "CZCE")   # 普麦
    # download_history_data("CF911", "CZCE")   # 一号棉
    # download_history_data("MA909", "CZCE")   # 甲醇
    download_history_data("CF005", "CZCE")   # 一号棉


    # 上期所
    # download_history_data("NI99", "SHFE")
    # download_history_data("AU99", "SHFE")
    # download_history_data("SN99", "SHFE")
    # download_history_data("AG99", "SHFE")
    # download_history_data("RB99", "SHFE")
    # download_history_data("WR99", "SHFE")
    # download_history_data("HC99", "SHFE")
    # download_history_data("SC99", "SHFE")
    # download_history_data("BU99", "SHFE")
    # download_history_data("RU99", "SHFE")

    # 中金所
    # download_history_data("IF99", "CFFEX")
    # download_history_data("IC99", "CFFEX")
    # download_history_data("IH99", "CFFEX")

    # 大商所
    # download_history_data("C99", "DCE")
    # download_history_data("CS99", "DCE")
    # download_history_data("A99", "DCE")
    # download_history_data("B99", "DCE")
    # download_history_data("M99", "DCE")
    # download_history_data("Y99", "DCE")
    # download_history_data("P99", "DCE")
    # download_history_data("FB99", "DCE")
    # download_history_data("BB99", "DCE")
    # download_history_data("JD99", "DCE")
    # download_history_data("L99", "DCE")
    # download_history_data("V99", "DCE")
    # download_history_data("PP99", "DCE")
    # download_history_data("J99", "DCE")
    # download_history_data("JM99", "DCE")
    # download_history_data("I99", "DCE")

    # 郑商所
    # download_history_data("TA99", "CZCE")
    # download_history_data("MA99", "CZCE")
    # download_history_data("FG99", "CZCE")
    # download_history_data("SF99", "CZCE")
    # download_history_data("SM99", "CZCE")
    # download_history_data("ZC99", "CZCE")
    # download_history_data("WH99", "CZCE")
    # download_history_data("PM99", "CZCE")
    # download_history_data("CF99", "CZCE")
    # download_history_data("SR99", "CZCE")
    # download_history_data("OI99", "CZCE")
    # download_history_data("RI99", "CZCE")
    # download_history_data("RS99", "CZCE")
    # download_history_data("RM99", "CZCE")
    # download_history_data("JR99", "CZCE")
    # download_history_data("LR99", "CZCE")
    # download_history_data("CY99", "CZCE")
    # download_history_data("AP99", "CZCE")
