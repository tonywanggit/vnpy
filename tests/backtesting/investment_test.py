# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 9:22
# @Author  : Tony
"""Description"""

from datetime import datetime

from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.base import EngineType
from vnpy.app.investment_manager.template import CtaInvestmentTemplate
from vnpy.trader.constant import Exchange, Direction, Offset
from vnpy.trader.database.investment.base import TradeDataExt

engine = BacktestingEngine()
investment_template = CtaInvestmentTemplate(engine, "TONY001", "TONY001", {})


def build_trade(offset: Offset, volume: int, price: float):
    return TradeDataExt(
        symbol="TONY001",
        product_code="TONY",
        strategy="TEST",
        exchange=Exchange.SHFE,
        direction=Direction.LONG,
        offset=offset,
        time=datetime.now().strftime("%H:%M:%S"),
        datetime=datetime.now(),
        price=price,
        volume=volume,
        gateway_name="CTP",
        orderid="orderid",
        tradeid="tradeid",
        engine_type=EngineType.BACKTESTING
    )


if __name__ == '__main__':
    # trade = build_trade(Offset.OPEN, 2, 2000)
    # investment_template.start_investment(trade, 101)
    # investment_template.start_investment(trade, 102)

    trade = build_trade(Offset.CLOSE, 1, 2050)
    investment_template.finish_investment(trade, 103)
