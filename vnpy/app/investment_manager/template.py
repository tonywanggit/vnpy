# -*- coding: utf-8 -*-
# @Time    : 2019/10/1 16:11
# @Author  : Tony
import re
from datetime import datetime, timedelta

from vnpy.app.cta_strategy import CtaTemplate
from vnpy.app.cta_strategy.base import EngineType
from vnpy.event import EventEngine, Event
from vnpy.trader.constant import Offset, Direction
from vnpy.trader.database import investment_database_manager
from vnpy.trader.object import TradeData
from .base import TradeDataExt, InvestmentData, InvestmentState, CommissionUnit

EVENT_RECORD_TRADE = "eRecordTrade"
EVENT_SEND_EMAIL = "eSendEmail"


class CtaInvestmentTemplate(CtaTemplate):
    """增加了投资记录的模板引擎"""

    # 投资记录自己的事件引擎，和主事件引擎分开，避免投资记录分析影响实盘交易
    investment_event_engine = EventEngine(10)
    start_event_engine = False

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(CtaInvestmentTemplate, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        if CtaInvestmentTemplate.start_event_engine == False:
            CtaInvestmentTemplate.start_event_engine = True
            CtaInvestmentTemplate.investment_event_engine.register(EVENT_RECORD_TRADE, self.process_record_trade)
            CtaInvestmentTemplate.investment_event_engine.register(EVENT_SEND_EMAIL, self.process_send_email)
            CtaInvestmentTemplate.investment_event_engine.start()

    def record_trade(self, trade: TradeData, strategy: str, send_email: bool = False):
        """
        记录交易数据
        """
        trade_data_ext = TradeDataExt.from_trade_data(trade)
        trade_data_ext.product_code = self.get_product_code(trade.symbol)
        trade_data_ext.strategy = strategy
        trade_data_ext.engine_type = self.get_engine_type()

        if self.get_engine_type() == EngineType.BACKTESTING:
            trade_data_ext.datetime = trade.datetime
        else:
            time_array = [int(i) for i in trade.time.split(":")]
            trade_data_ext.datetime = datetime.now().replace(hour=time_array[0],
                                                             minute=time_array[1],
                                                             second=time_array[2],
                                                             microsecond=0)
        CtaInvestmentTemplate.investment_event_engine.put(Event(EVENT_RECORD_TRADE, trade_data_ext))

        if send_email:
            CtaInvestmentTemplate.investment_event_engine.put(Event(EVENT_SEND_EMAIL, trade_data_ext))

    def process_record_trade(self, event: Event):
        trade_data: TradeDataExt = event.data
        trade_id = investment_database_manager.save_trade_data(trade_data)

        if trade_data.offset == Offset.OPEN:
            self.start_investment(trade_data, trade_id)
        else:
            self.finish_investment(trade_data, trade_id)

    def start_investment(self, trade: TradeDataExt, trade_id: int):
        _, money_lock, cost_fee = self.get_moneylock_and_costfee(trade)

        investment = InvestmentData(
            open_trade_id=trade_id,
            symbol=trade.symbol,
            exchange=trade.exchange,
            product_code=trade.product_code,
            direction=trade.direction,
            start_datetime=trade.datetime,
            open_price=trade.price,
            volume=trade.volume,
            strategy=trade.strategy,
            engine_type=trade.engine_type,
            cost_fee=cost_fee,
            money_lock=money_lock
        )
        investment_database_manager.save_investment_data(investment)
        pass

    def finish_investment(self, trade: TradeDataExt, trade_id: int):
        # 回测的开始时间可能比较长支持10年，实盘100天足够了（基本投资都关闭了）
        start_time = datetime.now() - timedelta(days=100) if trade.engine_type == EngineType.LIVE \
            else datetime.now() - timedelta(days=3650)
        investment = investment_database_manager.get_investment(trade.symbol, trade.exchange, trade.engine_type.value,
                                                                start_time)
        if investment is None:
            print(f"找不到需要关闭的投资记录：{trade}")
            return

        investment.close_trade_ids = [trade_id]
        investment.end_datetime = trade.datetime
        investment.state = InvestmentState.FINISHED

        investment.finish_price = trade.price
        spread = trade.price - investment.open_price if investment.direction == Direction.LONG \
            else investment.open_price - trade.price

        product, _, cost_fee = self.get_moneylock_and_costfee(trade)
        investment.cost_fee += cost_fee
        investment.profit = spread * investment.volume * product.contract_size
        investment.net_profit = investment.profit - investment.cost_fee
        investment.profit_rate = investment.net_profit / investment.money_lock

        investment_database_manager.finish_investment(investment)

    def get_moneylock_and_costfee(self, trade: TradeDataExt):
        product = investment_database_manager.get_product(trade.product_code, trade.exchange)
        if product is None:
            self.write_log(f"找不到交易品种的配置信息{trade.product_code},请点击品种配置！")
            return None, 0, 0

        trade_amount = trade.price * trade.volume * product.contract_size
        money_lock = trade_amount * product.margin_percent
        cost_fee = trade_amount * product.commission if product.commission_unit == CommissionUnit.RATIO \
            else trade.volume * product.commission

        return product, money_lock, cost_fee

    def process_send_email(self, event: Event):
        trade_data: TradeDataExt = event.data
        self.send_email(str(trade_data))

    def get_product_code(self, symbol: str):
        matchObj = re.match(r'([a-zA-Z]+)', symbol, re.M | re.I)
        return matchObj.group(1).upper()
