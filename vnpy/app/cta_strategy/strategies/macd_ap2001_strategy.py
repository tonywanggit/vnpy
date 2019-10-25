# encoding: UTF-8

"""
MACD交易策略
"""
from vnpy.app.cta_strategy import (
    BarGenerator,
    ArrayManager,
    BarData,
    TickData
)
from vnpy.app.investment_manager.template import CtaInvestmentTemplate


class MacdAP001Strategy(CtaInvestmentTemplate):
    """基于布林通道的交易策略"""
    author = u'tonywang_efun'

    # 策略参数
    initDays = 15  # 初始化数据所用的天数
    fixedSize = 1  # 每次交易的数量
    fixWinPrcnt = 5  # 固定止盈百分比
    shortfixWinPrcnt = 5  # 固定止盈百分比

    # 公共策略变量
    posPrice = 0  # 持仓价
    macd = 0
    signal = 0
    hist = 0
    red_bar_num = 0
    green_bar_num = 0

    # 参数列表，保存了参数的名称
    parameters = ['initDays',
                  'fixedSize',
                  'fixWinPrcnt',
                  'shortfixWinPrcnt']

    # 变量列表，保存了变量的名称
    variables = ['posPrice',
                 'macd',
                 'signal',
                 'hist']

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(MacdAP001Strategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 1, self.on_xmin_bar)
        self.am = ArrayManager(50)

    # ----------------------------------------------------------------------
    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(self.initDays)

    # ----------------------------------------------------------------------
    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        self.put_event()

    # ----------------------------------------------------------------------
    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    # ----------------------------------------------------------------------
    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

    def on_xmin_bar(self, bar: BarData):
        """收到x分钟K线"""
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算多头指标数值
        self.macd, self.signal, self.hist = am.macd(12, 26, 9)

        if self.hist > 0:
            self.red_bar_num += 1
            self.green_bar_num = 0
        elif self.hist < 0:
            self.red_bar_num = 0
            self.green_bar_num += 1

        if self.red_bar_num == 1:
            print(bar.datetime, self.macd, self.signal, self.hist)

        # 当前无仓位，发送OCO开仓委托
        if self.pos == 0:
            self.intraTradeHigh = bar.high_price
            self.intraTradeLow = bar.low_price

            if self.hist > 0:
                self.buy(bar.close_price, self.fixedSize)

            elif self.hist < 0:
                self.short(bar.close_price, self.fixedSize)

        # 持有多头仓位
        elif self.pos > 0:
            if 0 < self.posPrice < bar.close_price \
                    and (bar.close_price - self.posPrice) / self.posPrice > (self.fixWinPrcnt / 100):
                self.sell(bar.close_price * 0.99, abs(self.pos))
            elif self.hist < 0:
                self.sell(bar.close_price * 0.99, abs(self.pos))
            else:
                self.intraTradeHigh = max(self.intraTradeHigh, bar.high_price)

        # 持有空头仓位
        elif self.pos < 0:
            if bar.close_price < self.posPrice \
                    and (self.posPrice - bar.close_price) / self.posPrice > (self.shortfixWinPrcnt / 100):
                self.cover(bar.close_price * 1.01, abs(self.pos))
            elif self.hist > 0:
                self.cover(bar.close_price * 1.01, abs(self.pos))
            else:
                self.intraTradeLow = min(self.intraTradeLow, bar.low_price)

        # 发出状态更新事件
        self.put_event()

    def on_order(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade):

        # 记录交易数据并分析投资情况
        self.record_trade(trade, "MACD", True)

        self.posPrice = trade.price
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop_order(self, so):
        """停止单推送"""
        pass
