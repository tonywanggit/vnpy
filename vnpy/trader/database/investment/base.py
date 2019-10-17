# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 15:34
# @Author  : Tony
"""投资管理用到的枚举和数据类型定义"""
from dataclasses import dataclass, field
from enum import Enum

from datetime import datetime

from vnpy.app.cta_strategy.base import EngineType
from vnpy.trader.constant import Direction, Exchange
from vnpy.trader.object import TradeData


class InvestmentState(Enum):
    PROGRESSING = "PROGRESSING"
    FINISHED = "FINISHED"


class CommissionUnit(Enum):
    ONE_HAND = "ONE_HAND"
    RATIO = "RATIO"


class InvestmentInterval(Enum):
    """
    投资周期
    """
    CurrentMonth = "当月"
    PreMonth = "上个月"
    Today = "今天"
    Yesterday = "昨天"
    NearlyMonth = "近一个月"
    NearlyWeek = "近一个周"


@dataclass
class ProductData:
    """期货品种"""
    exchange: Exchange
    product_code: str
    product_name: str
    contract_size: float
    margin_percent: float
    commission_unit: CommissionUnit
    commission: float


@dataclass
class InvestmentData:
    """投资记录"""
    id: int = None
    product_code: str = None
    symbol: str = None
    exchange: Exchange = None

    start_datetime: datetime = None
    end_datetime: datetime = None
    direction: Direction = None
    volume: float = None
    close_volume: float = None
    open_price: float = None
    finish_price: float = None

    money_lock: float = None  # 资金占用
    profit: float = None  # 毛利润
    cost_fee: float = None  # 手续费
    net_profit: float = None  # 净利润 = 毛利润 - 手续费
    profit_rate: float = None  # 利润率 = 净利润

    state: InvestmentState = InvestmentState.PROGRESSING
    strategy: str = None
    open_trade_id: int = None
    close_trade_ids: list = field(default_factory=list)
    engine_type: EngineType = None


@dataclass
class TradeDataExt(TradeData):
    """交易记录"""
    id: int = 0
    datetime: datetime = None
    product_code: str = None
    strategy: str = None
    engine_type: EngineType = None
    rest_volume: int = 0

    @staticmethod
    def from_trade_data(td: TradeData) -> "TradeDataExt":
        tdx = TradeDataExt(
            symbol=td.symbol,
            exchange=td.exchange,
            direction=td.direction,
            offset=td.offset,

            time=td.time,
            price=td.price,
            volume=td.volume,
            gateway_name=td.gateway_name,
            orderid=td.orderid,
            tradeid=td.tradeid
        )
        return tdx
