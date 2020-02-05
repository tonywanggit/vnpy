from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
    TickData,
    BarData,
    OrderData,
    TradeData,
    StopOrder
)

from .strategy_utility import AdvanceArrayManager

class BollingerShortXStrategy(CtaTemplate):
    """基于布林通道的交易策略"""
    author = u'tonywang_efun'

    # 策略参数
    bar_window = 13
    fixedSize = 2  # 每次交易的数量

    # （空头参数）
    shortBollLength = 58  # 通道窗口数
    shortEntryDev = 3.5  # 开仓偏差
    shortExitDev = 2.9  # 平仓偏差
    shortTrailingPrcnt = 1.2  # 移动止损百分比
    shortMaLength = 42  # 过滤用均线窗口

    # 策略变量(空头)
    shortEntryLine = 0  # 开仓上轨
    shortExitLine = 0  # 平仓上轨
    shortMaFilter = 0  # 均线过滤
    shortMaFilterPrevious = 0  # 上一期均线
    intraTradeLow = 0  # 持仓期内的最最低点
    shortEntry = 0  # 空头开仓
    shortExit = 0  # 空头平仓

    # 参数列表，保存了参数的名称
    parameters = ['fixedSize',
                  'bar_window',
                  'shortBollLength',
                  'shortEntryDev',
                  'shortExitDev',
                  'shortTrailingPrcnt',
                  'shortMaLength']

    # 变量列表，保存了变量的名称
    variables = ['shortEntryLine',
                 'shortExitLine',
                 'shortEntry',
                 'shortExit',
                 'intraTradeHigh',
                 'intraTradeLow']

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, self.bar_window, self.on_xmin_bar)
        self.am = AdvanceArrayManager()

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
        self.bg.update_bar(bar)

    def on_xmin_bar(self, bar: BarData):
        """收到x分钟K线"""
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算空头指标数值
        self.shortEntryLine, self.shortExitLine = am.boll_double_down(self.shortBollLength, self.shortEntryDev,
                                                                      self.shortExitDev)
        short_ma_array = am.sma(self.shortMaLength, True)
        self.shortMaFilter = short_ma_array[-1]
        self.shortMaFilterPrevious = short_ma_array[-2]

        # 当前无仓位，发送OCO开仓委托
        if self.pos == 0:
            self.intraTradeHigh = bar.high_price
            self.intraTradeLow = bar.low_price
			
            if bar.close_price < self.shortMaFilter < self.shortMaFilterPrevious:
                self.shortEntry = self.shortEntryLine
                self.short(self.shortEntry, self.fixedSize, True)

        # 持有空头仓位
        elif self.pos < 0:
            self.intraTradeLow = min(self.intraTradeLow, bar.low_price)
            self.shortExit = self.intraTradeLow * (1 + self.shortTrailingPrcnt / 100)
            self.shortExit = max(self.shortExit, self.shortExitLine)

            self.cover(self.shortExit, abs(self.pos), True)

        # 发出状态更新事件
        self.put_event()

    def on_order(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade):
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop_order(self, so):
        """停止单推送"""
        pass
