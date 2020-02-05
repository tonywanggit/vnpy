from vnpy.gateway.bitmex import BitmexGateway
from vnpy.app.cta_backtester import CtaBacktesterApp
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.investment_manager import InvestmentManagerApp
from vnpy.app.risk_manager import RiskManagerApp
from vnpy.app.spread_trading import SpreadTradingApp
from vnpy.event import EventEngine
from vnpy.gateway.ctp import CtpGateway
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp


# from vnpy.gateway.femas import FemasGateway


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(BitmexGateway)
    main_engine.add_gateway(CtpGateway)

    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(SpreadTradingApp)
    # main_engine.add_app(CsvLoaderApp)
    # main_engine.add_app(AlgoTradingApp)
    # main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(InvestmentManagerApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
