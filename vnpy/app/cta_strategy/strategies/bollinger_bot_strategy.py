# encoding: UTF-8

"""
仅在知乎Live《vn.py的过去、现在和将来》中分享，请勿外传。

基于布林通道通道的交易策略，适合用在股指上5分钟线上。
"""

from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
    BarData,
    TickData
)


class BollingerBotStrategy(CtaTemplate):
    """基于布林通道的交易策略"""
    author = u'tonywang_efun'

    # 策略参数
    bollLength = 40  # 通道窗口数
    entryDev = 3.2  # 开仓偏差
    exitDev = 1.2  # 平仓偏差
    trailingPrcnt = 0.6  # 移动止损百分比
    maLength = 13  # 过滤用均线窗口
    initDays = 10  # 初始化数据所用的天数
    fixedSize = 1  # 每次交易的数量

    # 策略变量
    entryUp = 0  # 开仓上轨
    exitUp = 0  # 平仓上轨
    maFilter = 0  # 均线过滤
    maFilter1 = 0  # 上一期均线
    intraTradeHigh = 0  # 持仓期内的最高点
    longEntry = 0  # 多头开仓
    longExit = 0  # 多头平仓

    # 参数列表，保存了参数的名称
    parameters = ['bollLength',
                  'entryDev',
                  'exitDev',
                  'trailingPrcnt',
                  'maLength',
                  'initDays',
                  'fixedSize']

    # 变量列表，保存了变量的名称
    variables = ['entryUp',
                 'exitUp',
                 'intraTradeHigh',
                 'longEntry',
                 'shortEntry']

    # ----------------------------------------------------------------------
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(BollingerBotStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = ArrayManager(40)

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

        # 计算指标数值
        self.entryUp, self.exitUp = am.boll_double_up(self.bollLength, self.entryDev, self.exitDev)
        ma_array = am.sma(self.maLength, True)
        self.maFilter = ma_array[-1]
        self.maFilter1 = ma_array[-2]

        # 当前无仓位，发送OCO开仓委托
        if self.pos == 0:
            self.intraTradeHigh = bar.high_price

            if bar.close_price > self.maFilter > self.maFilter1:
                self.longEntry = self.entryUp
                self.buy(self.longEntry, self.fixedSize, True)

        # 持有多头仓位
        elif self.pos > 0:
            self.intraTradeHigh = max(self.intraTradeHigh, bar.high_price)

            self.longExit = self.intraTradeHigh * (1 - self.trailingPrcnt / 100)
            self.longExit = min(self.longExit, self.exitUp)

            self.sell(self.longExit, abs(self.pos), True)

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
