# encoding: UTF-8

"""
基于布林通道的双边交易策略
"""

from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
    BarData,
    TickData
)


class BollingerBotTonyStrategy(CtaTemplate):
    """基于布林通道的交易策略"""
    author = u'tonywang_efun'

    # 策略参数
    fixedSize = 2  # 每次交易的数量
    initDays = 10  # 初始化数据所用的天数

    # （多头参数）
    bollLength = 44  # 通道窗口数
    entryDev = 3.2  # 开仓偏差
    exitDev = 1.2  # 平仓偏差
    trailingPrcnt = 0.6  # 移动止损百分比
    maLength = 13  # 过滤用均线窗口

    # （空头参数）
    shortBollLength = 60  # 通道窗口数
    shortEntryDev = 3.6  # 开仓偏差
    shortExitDev = 0.7  # 平仓偏差
    shortTrailingPrcnt = 0.3  # 移动止损百分比
    shortMaLength = 18  # 过滤用均线窗口

    # 策略变量(多头)
    entryUp = 0  # 开仓上轨
    exitUp = 0  # 平仓上轨
    maFilter = 0  # 均线过滤
    maFilterPrevious = 0  # 上一期均线
    intraTradeHigh = 0  # 持仓期内的最高点
    longEntry = 0  # 多头开仓
    longExit = 0  # 多头平仓

    # 策略变量(空头)
    shortEntryUp = 0  # 开仓上轨
    shortExitUp = 0  # 平仓上轨
    shortMaFilter = 0  # 均线过滤
    shortMaFilterPrevious = 0  # 上一期均线
    intraTradeLow = 0  # 持仓期内的最最低点
    shortEntry = 0  # 空头开仓
    shortExit = 0  # 空头平仓

    # 参数列表，保存了参数的名称
    parameters = ['fixedSize',
                  'bollLength',
                  'entryDev',
                  'exitDev',
                  'trailingPrcnt',
                  'maLength',
                  'initDays',
                  'shortBollLength',
                  'shortEntryDev',
                  'shortExitDev',
                  'shortTrailingPrcnt',
                  'shortMaLength']

    # 变量列表，保存了变量的名称
    variables = ['entryUp',
                 'exitUp',
                 'intraTradeHigh',
                 'longEntry',
                 'longExit',
                 'shortEntryUp',
                 'shortExitUp',
                 'intraTradeLow',
                 'shortEntry',
                 'shortExit']

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BollingerBotTonyStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 6, self.on_5min_bar)
        self.am = ArrayManager(100)

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

    # ----------------------------------------------------------------------
    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

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

    def on_5min_bar(self, bar: BarData):
        """收到5分钟K线"""
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算多头指标数值
        self.entryUp, self.exitUp = am.boll_double_up(self.bollLength, self.entryDev, self.exitDev)
        ma_array = am.sma(self.maLength, True)
        self.maFilter = ma_array[-1]
        self.maFilterPrevious = ma_array[-2]

        # 计算空头指标数值
        self.shortEntryUp, self.shortExitUp = am.boll_double_down(self.shortBollLength, self.shortEntryDev,
                                                                  self.shortExitDev)
        short_ma_array = am.sma(self.shortMaLength, True)
        self.shortMaFilter = short_ma_array[-1]
        self.shortMaFilterPrevious = short_ma_array[-2]

        # 当前无仓位，发送OCO开仓委托
        if self.pos == 0:
            self.intraTradeHigh = bar.high_price
            self.intraTradeLow = bar.low_price

            if bar.close_price > self.maFilter > self.maFilterPrevious:
                self.longEntry = self.entryUp
                self.buy(self.longEntry, self.fixedSize, True)
            elif bar.close_price < self.shortMaFilter < self.shortMaFilterPrevious:
                self.shortEntry = self.shortEntryUp
                self.short(self.shortEntry, self.fixedSize, True)

        # 持有多头仓位
        elif self.pos > 0:
            self.intraTradeHigh = max(self.intraTradeHigh, bar.high_price)
            self.longExit = self.intraTradeHigh * (1 - self.trailingPrcnt / 100)
            self.longExit = min(self.longExit, self.exitUp)

            self.sell(self.longExit, abs(self.pos), True)

        # 持有空头仓位
        elif self.pos < 0:
            self.intraTradeLow = min(self.intraTradeLow, bar.low_price)
            self.shortExit = self.intraTradeLow * (1 - self.shortTrailingPrcnt / 100)
            self.shortExit = max(self.shortExit, self.shortExitUp)

            self.cover(self.shortExit, abs(self.pos), True)

        # 发出状态更新事件
        self.put_event()

    def on_order(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    # ----------------------------------------------------------------------
    def on_trade(self, trade):
        # 发出状态更新事件
        self.put_event()

    # ----------------------------------------------------------------------
    def on_stop_order(self, so):
        """停止单推送"""
        pass