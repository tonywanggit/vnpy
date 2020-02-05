# -*- coding: utf-8 -*-
# @Time    : 2019/12/22 11:14
# @Author  : Tony
"""实现多周期的批量回测"""

from datetime import datetime

from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.cinco_p2005_strategy import (
    CincoP2005Strategy
)

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="AG2005.SHFE",
    interval="1m",
    start=datetime(2010, 1, 1),
    end=datetime.now(),
    rate=2.25 / 10000,
    slippage=1,
    size=10,
    pricetick=1,
    capital=30000,
)
engine.add_strategy(CincoP2005Strategy, {})


engine.load_data()
engine.run_backtesting()
df = engine.calculate_result()
engine.calculate_statistics()


setting = OptimizationSetting()
setting.set_target("sharpe_ratio")
setting.add_parameter("boll_window", 16, 30, 2)
setting.add_parameter("boll_dev", 1.2, 3.2, 0.1)

result_values = engine.run_ga_optimization(setting)
print(result_values)

