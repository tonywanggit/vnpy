import pyqtgraph as pg
from PyQt5.QtWidgets import QHeaderView
from datetime import datetime, timedelta

from vnpy.event import Event, EventEngine
from vnpy.trader.database.investment.base import InvestmentInterval
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtCore, QtWidgets
from vnpy.trader.ui.widget import BaseMonitor, BaseCell, EnumCell, DirectionCell, DateTimeCell, PnlCell
from ..engine import (
    APP_NAME,
    EVENT_INVESTMENT_LOG
)


class InvestmentManager(QtWidgets.QWidget):
    """"""

    signal_log = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.investment_engine = main_engine.get_engine(APP_NAME)

        self.init_ui()
        self.register_event()

    def init_ui(self):
        """"""
        self.setWindowTitle("投资管理")

        # 设置UI组件
        self.interval_combo = QtWidgets.QComboBox()
        for inteval in InvestmentInterval:
            self.interval_combo.addItem(inteval.value)

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3 * 10)

        self.start_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate(
                start_dt.year,
                start_dt.month,
                start_dt.day
            )
        )
        self.end_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate.currentDate()
        )

        self.capital_line = QtWidgets.QLineEdit("30000")
        self.strategy_edit = QtWidgets.QLineEdit("")
        self.symbol_edit = QtWidgets.QLineEdit("")

        analyze_button = QtWidgets.QPushButton("开始统计")
        analyze_button.clicked.connect(self.start_analyzing)

        candle_button = QtWidgets.QPushButton("K线图表")
        candle_button.clicked.connect(self.show_candle_chart)

        product_manage_button = QtWidgets.QPushButton("品种维护")
        product_manage_button.clicked.connect(self.start_optimization)

        clean_backtester_button = QtWidgets.QPushButton("清空回测")
        clean_backtester_button.clicked.connect(self.start_optimization)

        for button in [
            analyze_button,
            product_manage_button,
            candle_button,
            clean_backtester_button
        ]:
            button.setFixedHeight(button.sizeHint().height() * 2)

        form = QtWidgets.QFormLayout()
        form.addRow("投资周期", self.interval_combo)
        form.addRow("投资策略", self.strategy_edit)
        form.addRow("投资品种", self.symbol_edit)
        form.addRow("投资金额", self.capital_line)
        form.addRow("开始日期", self.start_date_edit)
        form.addRow("结束日期", self.end_date_edit)

        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addLayout(form)
        left_vbox.addWidget(analyze_button)
        left_vbox.addWidget(candle_button)
        left_vbox.addStretch()
        left_vbox.addWidget(product_manage_button)
        left_vbox.addWidget(clean_backtester_button)
        left_vbox.addStretch()

        # Result part
        self.statistics_monitor = StatisticsMonitor()
        self.statistics_monitor.setMaximumHeight(310)

        self.investment_table = InvestmentTableMonitor(self.main_engine, self.event_engine)
        self.investment_table.setMinimumWidth(1550)
        # self.log_monitor.setMaximumHeight(900)

        self.chart = InvestmentChart()
        self.chart.setMinimumWidth(1200)
        self.chart.setMaximumHeight(310)

        # Layout
        center_top_hbox = QtWidgets.QHBoxLayout()
        center_top_hbox.addWidget(self.statistics_monitor)
        center_top_hbox.addWidget(self.chart)

        center_vbox = QtWidgets.QVBoxLayout()
        center_vbox.addLayout(center_top_hbox)
        center_vbox.addWidget(self.investment_table)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(center_vbox)
        self.setLayout(hbox)

    def show(self):
        """"""
        self.showMaximized()

    def register_event(self):
        """"""
        self.signal_log.connect(self.process_log_event)
        self.event_engine.register(EVENT_INVESTMENT_LOG, self.signal_log.emit)

    def process_log_event(self, event: Event):
        """"""
        msg = event.data
        self.write_log(msg)

    def write_log(self, msg):
        """"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"{timestamp}\t{msg}"
        self.investment_table.append(msg)

    def start_analyzing(self):
        """开始分析投资数据"""

        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        if end_date <= start_date:
            QtWidgets.QMessageBox.information(self, "友情提示", "结束日期必须大于开始日期！")

        investment_data = self.investment_engine.load_investment_data(start_date, end_date,
                                                                      self.strategy_edit.text(),
                                                                      self.symbol_edit.text())
        self.investment_table.update_data(investment_data)

        dataframe = self.investment_engine.build_pnl_dataframe(start_date, end_date, investment_data)
        self.chart.set_data(dataframe)

        statistics_map = self.investment_engine.build_statistics_map(investment_data)
        self.statistics_monitor.set_data(statistics_map)

        pass

    def start_optimization(self):
        """"""
        pass

    def start_downloading(self):
        """"""
        pass

    def show_candle_chart(self):
        """"""
        pass

    def show(self):
        """"""
        self.showMaximized()


class StatisticsMonitor(QtWidgets.QTableWidget):
    """"""
    KEY_NAME_MAP = {
        "start_num": "启动投资笔数",
        "finish_num": "结束投资笔数",
        "progressing_num": "进行中投资笔数",

        "profit_num": "盈利笔数",
        "drawdown_num": "回撤笔数",
        "max_profit": "单笔最大盈利",
        "max_drawdown": "单笔最大回撤",

        "total_money_lock": "资金占用",
        "total_net_pnl": "总盈亏",
        "total_commission": "总手续费"
    }

    def __init__(self):
        """"""
        super().__init__()

        self.cells = {}

        self.init_ui()

    def init_ui(self):
        """"""
        self.setRowCount(len(self.KEY_NAME_MAP))
        self.setVerticalHeaderLabels(list(self.KEY_NAME_MAP.values()))

        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.setEditTriggers(self.NoEditTriggers)

        for row, key in enumerate(self.KEY_NAME_MAP.keys()):
            cell = QtWidgets.QTableWidgetItem()
            self.setItem(row, 0, cell)
            self.cells[key] = cell

    def clear_data(self):
        """"""
        for cell in self.cells.values():
            cell.setText("")

    def set_data(self, data: dict):
        """"""
        data["total_money_lock"] = f"{data['total_money_lock']:,.2f}"
        data["total_net_pnl"] = f"{data['total_net_pnl']:,.2f}"
        data["total_commission"] = f"{data['total_commission']:,.2f}"
        data["max_profit"] = f"{data['max_profit']:,.2f}"
        data["max_drawdown"] = f"{data['max_drawdown']:,.2f}"

        for key, cell in self.cells.items():
            value = data.get(key, "")
            cell.setText(str(value))


class InvestmentChart(pg.GraphicsWindow):
    """"""

    def __init__(self):
        """"""
        super().__init__(title="Backtester Chart")

        self.dates = {}

        self.init_ui()

    def init_ui(self):
        """"""
        pg.setConfigOptions(antialias=True)

        self.pnl_plot = self.addPlot(
            title="每日盈亏",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom", maxTickLength=-10)}
        )

        zero_color = 'w'
        profit_color = 'r'
        loss_color = 'g'
        self.zero_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=zero_color, pen=zero_color
        )
        self.profit_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=profit_color, pen=profit_color
        )
        self.loss_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=loss_color, pen=loss_color
        )
        self.pnl_plot.addItem(self.zero_pnl_bar)
        self.pnl_plot.addItem(self.profit_pnl_bar)
        self.pnl_plot.addItem(self.loss_pnl_bar)

    def clear_data(self):
        """"""
        self.profit_pnl_bar.setOpts(x=[], height=[])
        self.loss_pnl_bar.setOpts(x=[], height=[])
        self.zero_pnl_bar.setOpts(x=[], height=[])

    def set_data(self, df):
        """"""
        self.clear_data()

        if df is None:
            return

        self.dates.clear()
        for n, date in enumerate(df["date"]):
            self.dates[n] = date

        # Set data for daily pnl bar
        zero_pnl_x = []
        zero_pnl_height = []
        profit_pnl_x = []
        profit_pnl_height = []
        loss_pnl_x = []
        loss_pnl_height = []

        for count, pnl in enumerate(df["net_pnl"]):
            if pnl > 0:
                profit_pnl_height.append(pnl)
                profit_pnl_x.append(count)
            elif pnl == 0:
                zero_pnl_height.append(pnl)
                zero_pnl_x.append(count)
            else:
                loss_pnl_height.append(pnl)
                loss_pnl_x.append(count)

        self.zero_pnl_bar.setOpts(x=zero_pnl_x, height=zero_pnl_height)
        self.profit_pnl_bar.setOpts(x=profit_pnl_x, height=profit_pnl_height)
        self.loss_pnl_bar.setOpts(x=loss_pnl_x, height=loss_pnl_height)


class DateAxis(pg.AxisItem):
    """Axis for showing date data"""

    def __init__(self, dates: dict, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.dates = dates

    def tickStrings(self, values, scale, spacing):
        """"""
        strings = []
        for v in values:
            dt = self.dates.get(v, "")
            strings.append(str(dt))
        return strings


class InvestmentTableMonitor(BaseMonitor):
    """
    投资记录列表
    """

    data_key = "id"
    sorting = True

    headers = {
        "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        "direction": {"display": "开仓方向", "cell": DirectionCell, "update": False},
        "open_price": {"display": "开仓价格", "cell": BaseCell, "update": False},
        "finish_price": {"display": "结束均价", "cell": BaseCell, "update": False},
        "volume": {"display": "数量", "cell": BaseCell, "update": False},
        "start_datetime": {"display": "开仓时间", "cell": DateTimeCell, "update": False},
        "end_datetime": {"display": "结束时间", "cell": DateTimeCell, "update": False},
        "money_lock": {"display": "资金占用", "cell": BaseCell, "update": False},
        "profit": {"display": "毛利", "cell": BaseCell, "update": False},
        "cost_fee": {"display": "手续费", "cell": BaseCell, "update": False},
        "net_profit": {"display": "净利", "cell": PnlCell, "update": False},
        "profit_rate": {"display": "净利率", "cell": BaseCell, "update": False},
        "state": {"display": "投资状态", "cell": EnumCell, "update": False},
        "strategy": {"display": "投资策略", "cell": BaseCell, "update": False},
    }

    def update_data(self, data: list):
        self.clear_data()
        data.reverse()
        for obj in data:
            self.insert_new_row(obj)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

    def clear_data(self):
        """"""
        self.setRowCount(0)
