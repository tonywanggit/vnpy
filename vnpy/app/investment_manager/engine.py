# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 14:36
# @Author  : Tony
"""投资管理核心逻辑"""

from datetime import date
from pandas import DataFrame

from vnpy.app.cta_strategy.base import EngineType
from vnpy.event import EventEngine
from vnpy.trader.database import investment_database_manager
from vnpy.trader.database.investment.base import InvestmentState
from vnpy.trader.engine import BaseEngine, MainEngine

APP_NAME = "InvestmentManager"
EVENT_INVESTMENT_LOG = "eInvestmentLog"


class InvestmentManagerEngine(BaseEngine):
    """投资管理引擎"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

    @staticmethod
    def load_investment_data(start_time: date, strategy: str, symbol: str):
        """加载投资数据"""
        return investment_database_manager.load_investment(strategy, symbol, EngineType.LIVE.value, start_time,
                                                           InvestmentState.FINISHED)

    @staticmethod
    def build_pnl_dataframe(investment_data_list):
        """构建每日盈亏数据"""
        pnl_dataframe = DataFrame(sorted(set([investment_data.date for investment_data in investment_data_list])),
                        columns=["date"])
        net_pnl = []
        for _, _date in enumerate(pnl_dataframe["date"]):
            net_pnl.append(sum(investment_data.net_profit for investment_data in
                               filter(lambda x: x.date == _date, investment_data_list)))
        pnl_dataframe["net_pnl"] = net_pnl

        return pnl_dataframe
