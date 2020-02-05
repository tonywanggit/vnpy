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


class CincoAtrStrategy(CtaTemplate):
    """"""

    author = "tonywang_efun"

    fixed_size = 1
    bar_window = 26
    boll_window = 39
    boll_dev = 1.9
    rsi_window = 10
    rsi_long = 74
    rsi_short = 37
    atr_window = 30
    atr_stop_multiplier = 1.5

    boll_up = 0
    boll_down = 0
    rsi_value = 0
    trading_size = 0
    intra_trade_high = 0
    intra_trade_low = 0
    long_stop = 0
    short_stop = 0
    atr_value = 0

    parameters = [
        "fixed_size",
        "bar_window",
        "boll_window",
        "boll_dev",
        "rsi_window",
        "rsi_long",
        "rsi_short",
        "atr_window",
        "atr_stop_multiplier"
    ]

    variables = [
        "boll_up",
        "boll_down",
        "rsi_value",
        "atr_value",
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
    
    def on_xmin_bar(self, bar: BarData):
        """"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self.rsi_value = self.am.rsi(self.rsi_window)
        self.atr_value = self.am.atr(self.atr_window)
        self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)

        if not self.pos:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price
            self.long_stop = 0
            self.short_stop = 0

            if self.rsi_value >= self.rsi_long:
                self.buy(self.boll_up, self.fixed_size, stop=True)

            if self.rsi_value <= self.rsi_short:
                self.short(self.boll_down, self.fixed_size, stop=True)
        
        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.long_stop = self.intra_trade_high - self.atr_value * self.atr_stop_multiplier
            self.sell(self.long_stop, abs(self.pos), stop=True)
        
        else:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.short_stop = self.intra_trade_low + self.atr_value * self.atr_stop_multiplier
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
