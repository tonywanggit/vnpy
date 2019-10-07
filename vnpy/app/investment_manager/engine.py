# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 14:36
# @Author  : Tony
"""投资管理核心逻辑"""

from collections import defaultdict
from vnpy.trader.object import OrderRequest, LogData
from vnpy.event import Event, EventEngine, EVENT_TIMER
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.event import EVENT_TRADE, EVENT_ORDER, EVENT_LOG
from vnpy.trader.constant import Status
from vnpy.trader.utility import load_json, save_json

APP_NAME = "InvestmentManager"


class InvestmentManagerEngine(BaseEngine):
    """投资管理引擎"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

