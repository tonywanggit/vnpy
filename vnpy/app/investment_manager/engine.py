# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 14:36
# @Author  : Tony
"""投资管理核心逻辑"""
from datetime import date

from vnpy.app.cta_strategy.base import EngineType
from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange
from vnpy.trader.database import investment_database_manager
from vnpy.trader.engine import BaseEngine, MainEngine

APP_NAME = "InvestmentManager"
EVENT_INVESTMENT_LOG = "eInvestmentLog"


class InvestmentManagerEngine(BaseEngine):
    """投资管理引擎"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

    def load_investment_data(self, start_time: date):
        """加载投资数据"""
        return investment_database_manager.get_investment(None, Exchange.SHFE, EngineType.LIVE.value, start_time)
