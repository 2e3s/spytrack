from datetime import datetime, timedelta
from typing import List, Dict

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem

from analyze import EventsAnalyzer
from analyze.matched_event import MatchedEvent
from analyze.stats import get_pie_chart, PieChartData
from gui.chart import Chart
from gui.ui import main
from config import ConfigStorage
from runner import Runner


class MainWindow(QtWidgets.QMainWindow):  # type: ignore
    ui: main.Ui_Main
    last_matched_events: List[MatchedEvent]

    def __init__(self, config_storage: ConfigStorage, stats_runner: Runner) -> None:
        super().__init__()
        self.stats_runner = stats_runner
        self.config = config_storage.load()
        self.config_storage = config_storage
        self.ui = main.Ui_Main()
        self.ui.setupUi(self)
        self.chart = Chart(self.config, self.ui.chartView)

        self.ui.projectsTimesList.itemSelectionChanged.connect(self._update_project_events)
        self.last_matched_events = []

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
        start_time = self._get_last_day_beginning(end_time)
        if start_time > end_time:
            start_time = start_time.replace(day=start_time.day - 1)
        self.ui.startDateTimeEdit.setDateTime(start_time)
        self.ui.endDateTimeEdit.setDateTime(end_time.replace())

        def _state_changed() -> None:
            self.ui.endDateTimeEdit.setDisabled(self.ui.disableDateRange.isChecked())
            self.ui.startDateTimeEdit.setDisabled(self.ui.disableDateRange.isChecked())
        self.ui.disableDateRange.stateChanged.connect(_state_changed)

    def _get_last_day_beginning(self, now_time: datetime) -> datetime:
        (hours, minutes) = self.config.start_date_time.split(':')
        start_time = now_time.replace(hour=int(hours), minute=int(minutes), second=0)
        if start_time > now_time:
            start_time = start_time.replace(day=start_time.day - 1)
        return start_time

    def _run_timer(self) -> None:
        self._run_chart()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run_chart)
        self.timer.start(self.config.get_interval() * 1000)

    def _run_chart(self) -> None:
        analyzer = EventsAnalyzer(self.config)
        if self.ui.disableDateRange.isChecked():
            end_date = datetime.now()
            start_date = self._get_last_day_beginning(end_date)
        else:
            start_date = self.ui.startDateTimeEdit.dateTime().toPyDateTime()
            end_date = self.ui.endDateTimeEdit.dateTime().toPyDateTime()

        events = analyzer.get_events(start_date, end_date)
        self.last_matched_events = analyzer.match(events, self.config.projects, self.config.none_project)
        chart_data = get_pie_chart(self.last_matched_events)
        self.chart.draw(chart_data)
        self._run_projects(chart_data)

    def _update_project_events(self) -> None:
        self.ui.projectEventsList.clear()
        selected_items: List[QListWidgetItem] = self.ui.projectsTimesList.selectedItems()
        if len(selected_items) < 1:
            return
        if len(self.last_matched_events) < 1:
            return
        selected_project = selected_items[0].data(Qt.UserRole)
        i = 0
        items = []
        for event in self.last_matched_events[::-1]:
            if event.project == selected_project:
                text = ', '.join(["{}={}".format(key, value) for key, value in event.event.data.items()])
                text = '{}: {}'.format(int(event.event.duration.total_seconds()), text)
                items.append(text)
                i += 1
                if i > 500:
                    break
        self.ui.projectEventsList.addItems(items)

    def _run_projects(self, chart_data: PieChartData) -> None:
        existing_projects: Dict[str, QListWidgetItem] = {}
        for i in range(0, self.ui.projectsTimesList.count()):
            item: QListWidgetItem = self.ui.projectsTimesList.item(i)
            existing_projects[str(item.data(Qt.UserRole))] = item

        for project, duration in chart_data.data.items():
            if project not in existing_projects:
                item = QListWidgetItem()
                item.setData(Qt.UserRole, project)
                self.ui.projectsTimesList.addItem(item)
            else:
                item = existing_projects[project]
            item.setText("{} ({})".format(
                self._format_project_name(project),
                str(timedelta(seconds=int(duration)))
            ))
        self._update_project_events()

    def _format_project_name(self, project_name: str) -> str:
        if project_name == self.config.none_project:
            return 'None'
        else:
            return project_name

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
