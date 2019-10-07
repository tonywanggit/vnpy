# -*- coding: utf-8 -*-
# @Time    : 2019/9/29 9:18
# @Author  : Tony
"""投资管理数据库接口"""
from abc import ABC, abstractmethod

from typing import Sequence, TYPE_CHECKING

from vnpy.trader.constant import Exchange

if TYPE_CHECKING:
    from vnpy.app.investment_manager.base import TradeDataExt, InvestmentData, ProductData  # noqa


class InvestmentDatabaseManager(ABC):

    @abstractmethod
    def save_trade_data(self, data: "TradeDataExt") -> int:
        pass

    @abstractmethod
    def save_investment_data(self, data: "InvestmentData") -> int:
        pass

    @abstractmethod
    def get_investment(self, symbol:str, exchange:Exchange, engine_type:str) -> "InvestmentData":
        pass

    @abstractmethod
    def finish_investment(self, data: "InvestmentData"):
        pass

    @abstractmethod
    def save_product_data(self, data: "ProductData") -> int:
        pass

    @abstractmethod
    def load_all_product(self) -> Sequence["ProductData"]:
        pass

    @abstractmethod
    def get_product(self, product_code:str, exchange:Exchange) -> "ProductData":
        pass
