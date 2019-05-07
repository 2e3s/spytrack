from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from analyze import EventsAnalyzer
from gui.chart import Chart
from gui.ui import main
from config import ConfigStorage
from runner import Runner


class MainWindow(QtWidgets.QMainWindow):  # type: ignore
    ui: main.Ui_Main

    def __init__(self, config_storage: ConfigStorage, stats_runner: Runner) -> None:
        super().__init__()
        self.stats_runner = stats_runner
        self.config = config_storage.load()
        self.config_storage = config_storage
        self.ui = main.Ui_Main()
        self.ui.setupUi(self)
        self.chart = Chart(self.config, self.ui.chartView)

        self._setup_settings()
        self._setup_datetime()
        self._run_timer()

    def _setup_settings(self) -> None:
        self.ui.portBox.setValue(self.config.get_port())
        self.ui.intervalBox.setValue(self.config.get_interval())
        self.ui.hostEdit.setText(self.config.get_host())

        def _state_changed() -> None:
            self.ui.hostEdit.setDisabled(self.ui.isLocalServerBox.isChecked())
        self.ui.isLocalServerBox.stateChanged.connect(_state_changed)
        self.ui.isLocalServerBox\
            .setCheckState(QtCore.Qt.Checked if self.config.is_run_server() else QtCore.Qt.Unchecked)
        self.ui.applyButton.clicked.connect(self._modify_config)

    def _setup_datetime(self) -> None:
        end_time = datetime.now().replace(microsecond=0)
        start_time = end_time.replace(hour=6, minute=0, second=0)
        if start_time > end_time:
            start_time = start_time.replace(day=start_time.day - 1)
        self.ui.startDateTimeEdit.setDateTime(start_time)
        self.ui.endDateTimeEdit.setDateTime(end_time.replace())

        def _state_changed() -> None:
            self.ui.endDateTimeEdit.setDisabled(self.ui.enableEndDate.isChecked())
        self.ui.enableEndDate.stateChanged.connect(_state_changed)

    def _run_timer(self) -> None:
        self._run_chart()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run_chart)
        self.timer.start(self.config.get_interval() * 1000)

    def _run_chart(self) -> None:
        analyzer = EventsAnalyzer(self.config)
        start_date: datetime = self.ui.startDateTimeEdit.dateTime().toPyDateTime()
        if self.ui.enableEndDate.isChecked():
            end_date = datetime.now()
        else:
            end_date = self.ui.endDateTimeEdit.dateTime().toPyDateTime()

        events = analyzer.get_events(start_date, end_date)
        matched_events = analyzer.match(events, self.config.projects, self.config.none_project)
        self.chart.draw(matched_events)

    def _modify_config(self) -> None:
        self.ui.applyButton.setDisabled(True)
        self.timer.stop()

        self.config.set_port(self.ui.portBox.value())
        self.config.set_host(self.ui.hostEdit.text())
        self.config.set_interval(self.ui.intervalBox.value())
        self.config.set_run_server(self.ui.isLocalServerBox.isChecked())

        self.config_storage.save(self.config)
        self.stats_runner.reload(self.config)
        self.chart.reload_config(self.config)
        self.timer.start(self.config.get_interval() * 1000)
        self.ui.applyButton.setDisabled(False)
