# -*- coding: utf-8 -*-
# @Time    : 2019/9/29 8:46
# @Author  : Tony
"""投资管理的数据库SQL实现"""
from datetime import datetime
from peewee import (
    AutoField,
    CharField,
    Database,
    DateTimeField,
    FloatField,
    Model)
from typing import Sequence, Type

from vnpy.app.cta_strategy.base import EngineType
from vnpy.trader.constant import Exchange, Direction, Offset
from vnpy.trader.database.investment.base import TradeDataExt, InvestmentData, ProductData, CommissionUnit, \
    InvestmentState
from .database import InvestmentDatabaseManager
from ..database import Driver
from ..database_sql import ModelBase, init_mysql, init_sqlite, init_postgresql


def init(driver: Driver, settings: dict):
    init_funcs = {
        Driver.SQLITE: init_sqlite,
        Driver.MYSQL: init_mysql,
        Driver.POSTGRESQL: init_postgresql,
    }
    assert driver in init_funcs

    db = init_funcs[driver](settings)
    trade, investment, product = init_models(db, driver)
    return InvestmentSqlManager(trade, investment, product)


def init_models(db: Database, driver: Driver):
    class DbTradeData(ModelBase):
        """
        交易记录
        """
        id = AutoField()
        symbol: str = CharField()
        product_code: str = CharField()
        exchange: str = CharField()
        datetime: datetime = DateTimeField()

        direction: str = CharField()
        offset: str = CharField()
        price: float = FloatField()
        volume: float = FloatField()
        rest_volume: float = FloatField()
        strategy: str = CharField()
        engine_type: str = CharField()

        class Meta:
            database = db
            db_table = "dbtrade"
            indexes = ((("datetime", "engine_type", "symbol", "exchange"), False),)

        @staticmethod
        def from_trade(trade: TradeDataExt):
            """
            Generate DbTradeData object from TradeData.
            """
            db_trade = DbTradeData()
            db_trade.product_code = trade.product_code
            db_trade.symbol = trade.symbol
            db_trade.exchange = trade.exchange.value
            db_trade.datetime = trade.datetime
            db_trade.offset = trade.offset.value
            db_trade.direction = trade.direction.value
            db_trade.volume = trade.volume
            db_trade.rest_volume = trade.volume  # 剩余需要开平配对的数量
            db_trade.price = trade.price
            db_trade.strategy = trade.strategy
            db_trade.engine_type = trade.engine_type.value

            return db_trade

        def to_trade(self):
            trade = TradeDataExt(
                id=self.id,
                product_code=self.product_code,
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                datetime=self.datetime,
                direction=Direction(self.direction),
                offset=Offset(self.offset),
                price=self.price,
                volume=self.volume,
                rest_volume=self.rest_volume,
                strategy=self.strategy,
                engine_type=EngineType(self.engine_type)
            )
            return trade

        @staticmethod
        def save_one(product: "DbTradeData") -> int:
            record = product.to_dict()
            return DbTradeData.insert(record).execute()

    class DbInvestmentData(ModelBase):
        """
        投资记录
        """
        id = AutoField()
        product_code: str = CharField()
        symbol: str = CharField()
        exchange: str = CharField()

        start_datetime: datetime = DateTimeField()
        end_datetime: datetime = DateTimeField(null=True)

        direction: str = CharField()
        volume: float = FloatField()
        close_volume: float = FloatField()

        open_price: float = FloatField()
        finish_price: float = FloatField(null=True)  # 多笔平仓价的均价

        money_lock: float = FloatField(null=True)  # 资金占用
        profit: float = FloatField(null=True)  # 毛利润
        cost_fee: float = FloatField(null=True)  # 手续费
        net_profit: float = FloatField(null=True)  # 净利润 = 毛利润 - 手续费
        profit_rate: float = FloatField(null=True)  # 利润率 = 净利润 /

        open_trade_id: int = CharField()
        close_trade_ids: str = CharField(null=True)

        strategy: str = CharField()
        state: int = CharField()
        engine_type: str = CharField()

        class Meta:
            database = db
            db_table = "dbinvestment"
            indexes = ((("start_datetime", "engine_type", "state", "symbol", "exchange"), False),)

        @staticmethod
        def from_investment(investment: InvestmentData):
            db_investment = DbInvestmentData()
            db_investment.id = investment.id if investment.id is not None and investment.id > 0 else None
            db_investment.product_code = investment.product_code
            db_investment.symbol = investment.symbol
            db_investment.exchange = investment.exchange.value
            db_investment.open_price = investment.open_price
            db_investment.finish_price = investment.finish_price
            db_investment.volume = investment.volume
            db_investment.close_volume = investment.close_volume
            db_investment.direction = investment.direction.value

            db_investment.money_lock = investment.money_lock
            db_investment.profit = investment.profit
            db_investment.profit_rate = investment.profit_rate
            db_investment.net_profit = investment.net_profit
            db_investment.cost_fee = investment.cost_fee
            db_investment.strategy = investment.strategy
            db_investment.start_datetime = investment.start_datetime
            db_investment.end_datetime = investment.end_datetime
            db_investment.open_trade_id = investment.open_trade_id
            if len(investment.close_trade_ids) > 0:
                db_investment.close_trade_ids = ",".join([str(x) for x in investment.close_trade_ids])

            db_investment.state = investment.state.value
            db_investment.engine_type = investment.engine_type.value

            return db_investment

        def to_investment(self):
            investment = InvestmentData(
                id=self.id,
                exchange=Exchange(self.exchange),
                product_code=self.product_code,
                symbol=self.symbol,
                open_price=self.open_price,
                finish_price=self.finish_price,
                volume=self.volume,
                close_volume=self.close_volume,
                direction=Direction(self.direction),

                money_lock=self.money_lock,
                profit=self.profit,
                profit_rate=self.profit_rate,
                net_profit=self.net_profit,
                cost_fee=self.cost_fee,
                strategy=self.strategy,
                start_datetime=self.start_datetime,
                end_datetime=self.end_datetime,
                open_trade_id=self.open_trade_id,
                close_trade_ids=self.close_trade_ids.split(",") if self.close_trade_ids is not None else None,
                state=InvestmentState(self.state),
                engine_type=EngineType(self.engine_type)
            )
            return investment

        @staticmethod
        def save_one(product: "DbInvestmentData"):
            record = product.to_dict()
            DbInvestmentData.insert(record).execute()

    class DbProductData(ModelBase):
        """
        期货品种配置
        """
        id = AutoField()
        exchange: str = CharField()
        product_code: str = CharField()
        product_name: str = CharField()
        contract_size: float = FloatField()
        margin_percent: float = FloatField()
        commission_unit: str = CharField()
        commission: float = FloatField()

        class Meta:
            database = db
            db_table = "dbproduct"
            indexes = ((("exchange", "product_code"), True),)

        @staticmethod
        def from_product(product: ProductData):
            db_product = DbProductData()
            db_product.exchange = product.exchange.value
            db_product.product_code = product.product_code
            db_product.product_name = product.product_name
            db_product.contract_size = product.contract_size
            db_product.margin_percent = product.margin_percent
            db_product.commission_unit = product.commission_unit.value
            db_product.commission = product.commission
            return db_product

        def to_product(self):
            product = ProductData(
                exchange=Exchange(self.exchange),
                product_code=self.product_code,
                product_name=self.product_name,
                contract_size=self.contract_size,
                margin_percent=self.margin_percent,
                commission_unit=CommissionUnit(self.commission_unit),
                commission=self.commission
            )
            return product

        @staticmethod
        def save_one(product: "DbProductData"):
            record = product.to_dict()
            if driver is Driver.POSTGRESQL:
                return DbProductData.insert(record).on_conflict(
                    action="IGNORE",
                    update=record,
                    conflict_target=(
                        DbProductData.exchange,
                        DbProductData.product_code
                    ),
                ).execute()
            else:
                return DbProductData.insert(record).on_conflict_ignore().execute()

    db.connect()
    db.create_tables([DbTradeData, DbInvestmentData, DbProductData])
    return DbTradeData, DbInvestmentData, DbProductData


class InvestmentSqlManager(InvestmentDatabaseManager):

    def __init__(self, class_trade: Type[Model], class_investment: Type[Model], class_product: Type[Model]):
        self.class_trade = class_trade
        self.class_investment = class_investment
        self.class_product = class_product

    def save_trade_data(self, data: TradeDataExt) -> int:
        trade = self.class_trade.from_trade(data)
        return self.class_trade.save_one(trade)

    def save_investment_data(self, data: InvestmentData) -> int:
        investment = self.class_investment.from_investment(data)
        self.class_investment.save_one(investment)

    def get_investment(self, symbol: str, exchange: Exchange, engine_type: str, start_time: datetime) -> InvestmentData:
        s = (
            self.class_investment.select().where(
                (self.class_investment.symbol == symbol)
                & (self.class_investment.exchange == exchange.value)
                & (self.class_investment.engine_type == engine_type)
                & (self.class_investment.state == InvestmentState.PROGRESSING.value)
                & (self.class_investment.start_datetime > start_time)
            ).order_by(self.class_investment.start_datetime.asc()).limit(1)
        )

        return s[0].to_investment() if s is not None and len(s) > 0 else None

    def load_investment(self, strategy: str, symbol: str, engine_type: str, start_time: datetime,
                        end_time: datetime, investment_state: InvestmentState) -> Sequence[InvestmentData]:
        investment_state_str = investment_state.value if investment_state is not None else ""

        end_time = datetime(end_time.year, end_time.month, end_time.day, hour=23, minute=59, second=59, microsecond=59)
        s = (
            self.class_investment.select().where(
                (((self.class_investment.symbol ** f'%{symbol}%') | (
                            self.class_investment.exchange ** f'%{symbol}%')) | (symbol is None or symbol.isspace()))
                & ((self.class_investment.strategy ** f'%{strategy}%') | (strategy is None or strategy.isspace()))
                & (self.class_investment.engine_type == engine_type)
                & ((self.class_investment.state == investment_state_str) | (investment_state is None))
                & (self.class_investment.start_datetime >= start_time)
                & (self.class_investment.start_datetime <= end_time)
            ).order_by(self.class_investment.start_datetime.asc())
        )
        # print(s)
        data = [db_investment.to_investment() for db_investment in s]
        return data

    def finish_investment(self, data: InvestmentData):
        investment = self.class_investment.from_investment(data)
        investment.save()

    def save_product_data(self, data: ProductData) -> int:
        product = self.class_product.from_product(data)
        return self.class_product.save_one(product)

    def load_all_product(self) -> Sequence["ProductData"]:
        s = (self.class_product.select())
        data = [db_product.to_product() for db_product in s]
        return data

    def get_product(self, product_code: str, exchange: Exchange) -> "ProductData":
        s = (self.class_product.select().where((self.class_product.product_code == product_code)
                                               & (self.class_product.exchange == exchange.value)))
        return s[0].to_product() if s is not None and len(s) > 0 else None

    def get_trade_data(self, trade_id: int) -> "TradeDataExt":
        s = (self.class_trade.select().where((self.class_trade.id == trade_id)))
        return s[0].to_trade() if s is not None and len(s) > 0 else None
