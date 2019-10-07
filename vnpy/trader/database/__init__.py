import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vnpy.trader.database.database import BaseDatabaseManager
    from vnpy.trader.database.investment.database import InvestmentDatabaseManager

if "VNPY_TESTING" not in os.environ:
    from vnpy.trader.setting import get_settings
    from .initialize import init
    from .investment.initialize import investment_init

    settings = get_settings("database.")
    database_manager: "BaseDatabaseManager" = init(settings=settings)
    investment_database_manager: "InvestmentDatabaseManager" = investment_init(settings=settings)
