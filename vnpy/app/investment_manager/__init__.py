from pathlib import Path
from vnpy.trader.app import BaseApp
from .engine import InvestmentManagerEngine, APP_NAME


class InvestmentManagerApp(BaseApp):
    """投资管理APP"""
    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "投资管理"
    engine_class = InvestmentManagerEngine
    widget_name = APP_NAME
    icon_name = "investment.ico"
