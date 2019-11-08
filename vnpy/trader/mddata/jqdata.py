import jqdatasdk as jq

from datetime import timedelta, datetime
from typing import List

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.mddata.dataapi import MdDataApi
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.setting import SETTINGS

INTERVAL_VT2JQ = {
    Interval.MINUTE: "1m",
    Interval.HOUR: "60m",
    Interval.DAILY: "1d",
}

INTERVAL_ADJUSTMENT_MAP_JQ = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta()  # no need to adjust for daily bar
}


class JqdataClient(MdDataApi):
    """聚宽JQData客户端封装类"""

    def __init__(self):
        """"""
        self.username = SETTINGS["jqdata.username"]
        self.password = SETTINGS["jqdata.password"]

        self.inited = False

    def init(self, username="", password=""):
        """"""
        if self.inited:
            return True

        if username and password:
            self.username = username
            self.password = password

        if not self.username or not self.password:
            return False

        try:
            jq.auth(self.username, self.password)
        except Exception as ex:
            print("jq auth fail:" + repr(ex))
            return False

        self.inited = True
        return True

    def to_jq_symbol(self, symbol: str, exchange: Exchange):
        """
        CZCE product of RQData has symbol like "TA1905" while
        vt symbol is "TA905.CZCE" so need to add "1" in symbol.
        """
        if exchange in [Exchange.SSE, Exchange.SZSE]:
            if exchange == Exchange.SSE:
                jq_symbol = f"{symbol}.XSHG"  # 上海证券交易所
            else:
                jq_symbol = f"{symbol}.XSHE"  # 深圳证券交易所
        elif exchange == Exchange.SHFE:
            jq_symbol = f"{symbol}.XSGE"  # 上期所
        elif exchange == Exchange.CFFEX:
            jq_symbol = f"{symbol}.CCFX"  # 中金所
        elif exchange == Exchange.DCE:
            jq_symbol = f"{symbol}.XDCE"  # 大商所
        elif exchange == Exchange.INE:
            jq_symbol = f"{symbol}.XINE"  # 上海国际能源期货交易所
        elif exchange == Exchange.CZCE:
            # 郑商所 的合约代码年份只有三位 需要特殊处理
            for count, word in enumerate(symbol):
                if word.isdigit():
                    break

            # Check for index symbol
            time_str = symbol[count:]
            if time_str in ["88", "888", "99"]:
                return symbol

            # noinspection PyUnboundLocalVariable
            product = symbol[:count]
            year = symbol[count]
            month = symbol[count + 1:]

            if year == "9":
                year = "1" + year
            else:
                year = "2" + year

            jq_symbol = f"{product}{year}{month}.XZCE"

        return jq_symbol.upper()

    def query_history(self, req: HistoryRequest):
        """
        Query history bar data from JQData.
        """
        symbol = req.symbol
        exchange = req.exchange
        interval = req.interval
        start = req.start
        end = req.end

        jq_symbol = self.to_jq_symbol(symbol, exchange)
        # if jq_symbol not in self.symbols:
        #     return None

        jq_interval = INTERVAL_VT2JQ.get(interval)
        if not jq_interval:
            return None

        # For adjust timestamp from bar close point (RQData) to open point (VN Trader)
        adjustment = INTERVAL_ADJUSTMENT_MAP_JQ.get(interval)

        # For querying night trading period data
        # end += timedelta(1)
        now = datetime.now()
        if end >= now:
            end = now
        elif end.year == now.year and end.month == now.month and end.day == now.day:
            end = now

        df = jq.get_price(
            jq_symbol,
            frequency=jq_interval,
            fields=["open", "high", "low", "close", "volume"],
            start_date=start,
            end_date=end,
            skip_paused=True
        )

        data: List[BarData] = []

        if df is not None:
            for ix, row in df.iterrows():
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=row.name.to_pydatetime() - adjustment,
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                    volume=row["volume"],
                    gateway_name="JQ"
                )
                data.append(bar)

        return data


jqdata_client = JqdataClient()
