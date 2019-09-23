from datetime import datetime

from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.mddata import mddata_client
from vnpy.trader.object import HistoryRequest


def download_history_data(symbol, exchange):
    print(symbol, exchange)
    begin_date = datetime.strptime("2019-09-19", "%Y-%m-%d")

    for i in range(1):
        start_date = begin_date.replace(year=begin_date.year + i)
        # end_date = begin_date.replace(year=begin_date.year + i + 1)
        end_date = datetime.now()

        print(start_date, end_date)
        req = HistoryRequest(
            symbol=symbol,
            exchange=Exchange(exchange),
            interval=Interval("1m"),
            start=start_date,
            end=end_date
        )
        data = mddata_client.query_history(req)


if __name__ == '__main__':
    mddata_client.init()

    download_history_data('RB1910', 'SHFE')
