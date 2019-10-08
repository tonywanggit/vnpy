# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 14:36
# @Author  : Tony
"""投资管理核心逻辑"""

from vnpy.event import EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine

APP_NAME = "InvestmentManager"
EVENT_INVESTMENT_LOG = "eInvestmentLog"


class InvestmentManagerEngine(BaseEngine):
    """投资管理引擎"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)
