from typing import List
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtChart import QPieSeries
from PyQt5.QtGui import QPainter

from analyze.stats import get_pie_chart
from analyze import EventsAnalyzer
from analyze.matched_event import MatchedEvent
from gui.ui import main
from config import ConfigStorage
from runner import Runner


class MainWindow(QtWidgets.QMainWindow):  # type: ignore
    ui: main.Ui_Main

    def __init__(self, config_storage: ConfigStorage, stats_runner: Runner) -> None:
        super(MainWindow, self).__init__()
        self.stats_runner = stats_runner
        self.config = config_storage.load()
        self.config_storage = config_storage
        self.ui = main.Ui_Main()
        self.ui.setupUi(self)

        self.ui.portBox.setValue(self.config.get_port())
        self.ui.intervalBox.setValue(self.config.get_interval())
        self.ui.hostEdit.setText(self.config.get_host())

        self.ui.isLocalServerBox.stateChanged.connect(self._state_changed)
        self.ui.isLocalServerBox\
            .setCheckState(QtCore.Qt.Checked if self.config.is_run_server() else QtCore.Qt.Unchecked)

        self.ui.applyButton.clicked.connect(self._modify_config)

        self._run_timer()

    def _run_chart(self) -> None:
        analyzer = EventsAnalyzer(self.config)
        events = analyzer.get_events()
        matched_events = analyzer.match(events, self.config.get_projects(), self.config.none_project)
        self.draw_chart(matched_events)

    def _run_timer(self) -> None:
        self._run_chart()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run_chart)
        self.timer.start(self.config.get_interval() * 1000)

    def _state_changed(self) -> None:
        self.ui.hostEdit.setDisabled(self.ui.isLocalServerBox.isChecked())

    def _modify_config(self) -> None:
        self.ui.applyButton.setDisabled(True)
        self.timer.stop()

        self.config.set_port(self.ui.portBox.value())
        self.config.set_host(self.ui.hostEdit.text())
        self.config.set_interval(self.ui.intervalBox.value())
        self.config.set_run_server(self.ui.isLocalServerBox.isChecked())

        self.config_storage.save(self.config)
        self.stats_runner.reload(self.config)
        self.timer.start(self.config.get_interval() * 1000)
        self.ui.applyButton.setDisabled(False)

    def draw_chart(self, matched_events: List[MatchedEvent]) -> None:
        chart_data = get_pie_chart(matched_events)
        series = QPieSeries()
        for project, duration in chart_data.data.items():
            series.append(project, duration)
        self.ui.chartView.setRenderHint(QPainter.Antialiasing)
        self.ui.chartView.chart().removeAllSeries()
        self.ui.chartView.chart().addSeries(series)
