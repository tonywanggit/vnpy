# encoding: UTF-8

"""
MACD交易策略
"""
from datetime import time

from vnpy.app.cta_strategy import (
    BarGenerator,
    ArrayManager,
    BarData,
    TickData,
    CtaTemplate)


class MacdStrategy(CtaTemplate):
    """基于布林通道的交易策略"""
    author = u'tonywang_efun'

    # 策略参数
    fixed_size = 1                    # 每次交易的数量
    fixed_long_win_percent = 0.5      # 固定止盈百分比（多头）
    fixed_short_win_percent = 0.5     # 固定止盈百分比（空头）

    # 公共策略变量
    pos_price = 0  # 持仓价
    intra_trade_high = 0
    intra_trade_low = 0
    macd = 0
    signal = 0
    hist = 0
    red_bar_num = 0
    green_bar_num = 0

    exit_time = time(hour=14, minute=55)
    night_open_time = time(hour=21, minute=00)
    last_bar = None
    new_day = False

    # 参数列表，保存了参数的名称
    parameters = ['fixed_size',
                  'fixed_long_win_percent',
                  'fixed_short_win_percent']

    # 变量列表，保存了变量的名称
    variables = ['pos_price',
                 'intra_trade_high',
                 'intra_trade_low',
                 'macd',
                 'signal',
                 'hist']

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 20, self.on_xmin_bar)
        self.am = ArrayManager()

    # ----------------------------------------------------------------------
    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

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
        if not self.last_bar or self.last_bar.datetime.date() != bar.datetime.date():
            self.new_day = True
        self.last_bar = bar

        self.bg.update_bar(bar)

        if self.pos > 0:
            if self.exit_time <= bar.datetime.time() <= self.night_open_time:
                self.sell(bar.close_price * 0.99, abs(self.pos))

        elif self.pos < 0:
            if self.exit_time <= bar.datetime.time() <= self.night_open_time:
                self.cover(bar.close_price * 1.01, abs(self.pos))

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

        if self.pos == 0 and (bar.datetime.time() < self.exit_time or bar.datetime.time() > self.night_open_time):
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.hist > 0:
                self.buy(bar.close_price, self.fixed_size)

            elif self.hist < 0:
                self.short(bar.close_price, self.fixed_size)

        # 持有多头仓位
        elif self.pos > 0:
            if self.pos_price > bar.close_price \
                    and (self.pos_price - bar.close_price) / self.pos_price > (self.fixed_long_win_percent / 100):
                self.sell(bar.close_price * 0.99, abs(self.pos))
            elif self.hist < 0:
                self.sell(bar.close_price * 0.99, abs(self.pos))
            else:
                self.intra_trade_high = max(self.intra_trade_high, bar.high_price)

        # 持有空头仓位
        elif self.pos < 0:
            if bar.close_price > self.pos_price \
                    and (bar.close_price - self.pos_price) / self.pos_price > (self.fixed_short_win_percent / 100):
                self.cover(bar.close_price * 1.01, abs(self.pos))
            elif self.hist > 0:
                self.cover(bar.close_price * 1.01, abs(self.pos))
            else:
                self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

        # 发出状态更新事件
        self.put_event()

    def on_order(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade):
        self.pos_price = trade.price
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop_order(self, so):
        """停止单推送"""
        pass
