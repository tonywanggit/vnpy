# -*- coding: utf-8 -*-
# @Time    : 2019/10/6 17:00
# @Author  : Tony
"""Description"""

import re

from vnpy.app.cta_strategy.base import EngineType
from vnpy.trader.constant import Exchange
from vnpy.trader.database import investment_database_manager
from vnpy.app.investment_manager.base import CommissionUnit, ProductData

# from vnpy.trader.constant import Exchange

def get_product_code(symbol: str):
    matchObj = re.match(r'([a-zA-Z]+)[0-9]*([a-zA-Z]+)', symbol, re.M | re.I)
    return matchObj.group(1)


def test_save_product():
    product = ProductData(
        exchange=Exchange.SHFE,
        product_code="TONY",
        product_name="TONY",
        contract_size=10,
        margin_percent=0.18,
        commission_unit=CommissionUnit.RATIO,
        commission=0.00015
    )
    return investment_database_manager.save_product_data(product)


if __name__ == '__main__':
    investment = investment_database_manager.get_investment("rb19101", Exchange.SHFE, EngineType.BACKTESTING)


    print(investment)