# -*- coding: utf-8 -*-
# @Time    : 2019/12/8 11:21
# @Author  : Tony
"""MongoDB数据倒入工具"""
from datetime import datetime, timedelta

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database.database import Driver, BaseDatabaseManager
from vnpy.trader.database.database_sql import init
from vnpy.trader.setting import get_settings

if __name__ == '__main__':
    sqllite_settings = {
        "database": "database.db"
    }

    sqllite_datamanager: BaseDatabaseManager = init(Driver.SQLITE, sqllite_settings)

    mysql_settings = get_settings("database.")
    mysql_datamanger: BaseDatabaseManager = init(Driver.MYSQL, mysql_settings)

    for year in range(2017, 2020):
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            bar_data = sqllite_datamanager.load_bar_data("XBTUSD", Exchange.BITMEX, Interval.MINUTE, start_date, end_date)
            print(start_date, end_date, len(bar_data))
            # mysql_datamanger.save_bar_data(bar_data)


