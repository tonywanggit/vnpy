# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 14:36
# @Author  : Tony
"""投资管理核心逻辑"""

from datetime import date, timedelta
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
    def load_investment_data(start_date: date, end_date: date, strategy: str, symbol: str):
        """加载投资数据"""
        return investment_database_manager.load_investment(strategy, symbol, EngineType.LIVE.value, start_date,
                                                           end_date, None)

    @staticmethod
    def build_pnl_dataframe(start_date: date, end_date: date, investment_data_list):
        """构建每日盈亏数据"""
        pnl_date = []
        _date = start_date
        while _date <= end_date:
            pnl_date.append(_date)
            _date += timedelta(1)
        pnl_dataframe = DataFrame(pnl_date, columns=["date"])

        net_pnl = []
        for _, _date in enumerate(pnl_dataframe["date"]):
            net_pnl.append(sum(investment_data.net_profit if investment_data.net_profit is not None else 0
                               for investment_data in filter(lambda x: x.date == _date, investment_data_list)))
        pnl_dataframe["net_pnl"] = net_pnl

        return pnl_dataframe

    @staticmethod
    def build_statistics_map(investment_data_list):
        start_num = 0
        finish_num = 0
        progressing_num = 0
        profit_num = 0
        drawdown_num = 0
        max_profit = 0
        max_drawdown = 0
        total_money_lock = 0
        total_net_pnl = 0
        total_commission = 0

        for investment in investment_data_list:
            start_num += 1
            total_net_pnl += investment.net_profit if investment.net_profit is not None else 0
            total_commission += investment.cost_fee

            if investment.state == InvestmentState.FINISHED:
                finish_num += 1
            elif investment.state == InvestmentState.PROGRESSING:
                progressing_num += 1
                total_money_lock += investment.money_lock

            if investment.net_profit is None:
                pass
            elif investment.net_profit > 0:
                profit_num += 1
                max_profit = max(max_profit, investment.net_profit)
            elif investment.net_profit < 0:
                drawdown_num += 1
                max_drawdown = max(max_drawdown, abs(investment.net_profit))

        statistics = {
            "start_num": start_num,
            "finish_num": finish_num,
            "progressing_num": progressing_num,
            "profit_num": profit_num,
            "drawdown_num": drawdown_num,
            "max_profit": max_profit,
            "max_drawdown": max_drawdown,
            "total_money_lock": total_money_lock,
            "total_net_pnl": total_net_pnl,
            "total_commission": total_commission
        }

        return statistics
