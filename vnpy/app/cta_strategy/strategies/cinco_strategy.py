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


class CincoStrategy(CtaTemplate):
    """"""

    author = "vnpy"

    boll_window = 42
    boll_dev = 2.2
    trailing_long = 0.65
    trailing_short = 0.65
    atr_window = 4
    risk_level = 300

    boll_up = 0
    boll_down = 0
    trading_size = 0
    intra_trade_high = 0
    intra_trade_low = 0
    long_stop = 0
    short_stop = 0
    atr_value = 0

    parameters = [
        "boll_window",
        "boll_dev",
        "trailing_long",
        "trailing_short",
        "atr_window",
        "risk_level"
    ]

    variables = [
        "boll_up",
        "boll_down",
        "trading_size",
        "intra_trade_high",
        "intra_trade_low",
        "long_stop",
        "short_stop",
        "atr_value"
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

        self.bg = BarGenerator(self.on_bar, 13, self.on_15min_bar)
        self.am = ArrayManager()

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
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)
    
    def on_15min_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.inited:
            return

        self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)
        boll_width = self.boll_up - self.boll_down

        if not self.pos:
            self.atr_value = self.am.atr(self.atr_window)
            self.trading_size = int(self.risk_level / self.atr_value)

            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.long_stop = 0
            self.short_stop = 0

            self.buy(self.boll_up, self.trading_size, stop=True)
            self.short(self.boll_down, self.trading_size, stop=True)
        
        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.long_stop = self.intra_trade_high - self.trailing_long * boll_width
            self.sell(self.long_stop, abs(self.pos), stop=True)
        
        else:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.short_stop = self.intra_trade_low + self.trailing_short * boll_width
            self.cover(self.short_stop, abs(self.pos), stop=True)
        
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
