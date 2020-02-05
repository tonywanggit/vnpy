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


class CincoZStrategy(CtaTemplate):
    """"""

    author = "tonywang_efun"

    bar_window = 13
    bar_z_window = 60
    boll_window = 38
    boll_dev = 2.2
    rsi_window = 8
    rsi_long = 76
    rsi_short = 18
    fast_window = 4
    slow_window = 26
    trailing_long = 2.8
    trailing_short = 2.6
    fixed_size = 2

    boll_up = 0
    boll_down = 0
    rsi_value = 0
    fast_ma = 0
    slow_ma = 0
    ma_trend = 0
    intra_trade_high = 0
    intra_trade_low = 0
    long_stop = 0
    short_stop = 0
    atr_value = 0

    parameters = [
        "bar_window",
        "bar_z_window",
        "boll_window",
        "boll_dev",
        "rsi_window",
        "rsi_long",
        "rsi_short",
        "fast_window",
        "slow_window",
        "trailing_long",
        "trailing_short",
        "fixed_size"
    ]

    variables = [
        "boll_up",
        "boll_down",
        "rsi_value",
        "fast_ma",
        "slow_ma",
        "ma_trend",
        "intra_trade_high",
        "intra_trade_low",
        "long_stop",
        "short_stop"
    ]

    def __init__(
        self,
        cta_engine,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, self.bar_window, self.on_xmin_bar)
        self.bgz = BarGenerator(self.on_bar, self.bar_z_window, self.on_zmin_bar)
        self.am = ArrayManager()
        self.amz = ArrayManager()

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)
    
    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
    
    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_bar(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)
        self.bgz.update_bar(bar)
    
    def on_xmin_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited or not self.amz.inited:
            return

        self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)
        self.rsi_value = self.am.rsi(self.rsi_window)
        boll_width = self.boll_up - self.boll_down

        if not self.pos:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.long_stop = 0
            self.short_stop = 0

            if self.ma_trend > 0 and self.rsi_value >= self.rsi_long:
                self.buy(self.boll_up, self.fixed_size, stop=True)

            if self.ma_trend < 0 and self.rsi_value <= self.rsi_short:
                self.short(self.boll_down, self.fixed_size, stop=True)
        
        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.long_stop = self.intra_trade_high - self.trailing_long * boll_width
            self.sell(self.long_stop, abs(self.pos), stop=True)
        
        else:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.short_stop = self.intra_trade_low + self.trailing_short * boll_width
            self.cover(self.short_stop, abs(self.pos), stop=True)
        
        self.put_event()

    def on_zmin_bar(self, bar: BarData):
        """"""
        self.amz.update_bar(bar)
        if not self.amz.inited:
            return

        self.fast_ma = self.amz.sma(self.fast_window)
        self.slow_ma = self.amz.sma(self.slow_window)

        if self.fast_ma > self.slow_ma:
            self.ma_trend = 1
        elif self.fast_ma < self.slow_ma:
            self.ma_trend = -1
        else:
            self.ma_trend = 0

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()
    
    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass
    
    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
