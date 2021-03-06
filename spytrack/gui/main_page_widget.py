from datetime import datetime, timedelta
from typing import List, Dict, Callable
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
from aw_client import ActivityWatchClient
from analyze.event_repository import EventRepository
from analyze.matched_event import MatchedEvent
from analyze import AnalyzerFacade
from analyze.stats import get_pie_chart, PieChartData
from config import Config, ConfigStorage
from gui.chart import Chart
from gui.settings_window import SettingsWindow
from .ui.main_page import Ui_MainPage

WidgetItems = List[QListWidgetItem]


class MainPageWidget(QtWidgets.QWidget):
    last_matched_events: List[MatchedEvent]

    def __init__(self,
                 config_storage: ConfigStorage,
                 reload_config: Callable[[Config], None]) -> None:
        super().__init__()
        self.external_reload_config = reload_config
        self.config_storage = config_storage
        self.config = config_storage.load()
        self.ui = Ui_MainPage()
        self.ui.setupUi(self)
        aw_client = ActivityWatchClient("gui", testing=False)
        self.events_repository = EventRepository(aw_client)

        self.chart = Chart(self.config, self.ui.chartView)
        self.ui.projectsTimesList.itemSelectionChanged.connect(
            self._update_project_events
        )
        self.ui.settingsButton.clicked.connect(self._show_settings)
        self.last_matched_events = []
        self.analyzer = AnalyzerFacade(self.events_repository, self.config)

        self._setup_datetime()
        self._run_timer()

    def _show_settings(self) -> None:
        settings_window = SettingsWindow(
            self.config,
            self.config_storage,
            self._reload_config
        )
        settings_window.exec_()

    def _reload_config(self, config: Config) -> None:
        self.external_reload_config(config)
        self.config = config
        self.timer.stop()
        self.analyzer = AnalyzerFacade(self.events_repository, config)
        self.chart.reload_config(config)
        self.timer.start(self.config.interval * 1000)

    def _setup_datetime(self) -> None:
        end_time = datetime.now().replace(microsecond=0)
        start_time = self._get_last_day_beginning(end_time)
        if start_time > end_time:
            start_time = start_time.replace(day=start_time.day - 1)
        self.ui.startDateTimeEdit.setDateTime(start_time)
        self.ui.endDateTimeEdit.setDateTime(end_time.replace())

        def state_changed() -> None:
            is_range_disabled = self.ui.disableDateRange.isChecked()
            self.ui.endDateTimeEdit.setDisabled(is_range_disabled)
            self.ui.startDateTimeEdit.setDisabled(is_range_disabled)
        self.ui.disableDateRange.stateChanged.connect(state_changed)

    def _get_last_day_beginning(self, now_time: datetime) -> datetime:
        (hours, minutes) = self.config.start_day_time.split(':')
        start_time = now_time.replace(hour=int(hours),
                                      minute=int(minutes),
                                      second=0)
        if start_time > now_time:
            start_time = start_time - timedelta(days=1)
        return start_time

    def _run_timer(self) -> None:
        self._run_chart()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run_chart)
        self.timer.start(self.config.interval * 1000)

    def _run_chart(self) -> None:
        if self.ui.disableDateRange.isChecked():
            end_date = datetime.now()
            start_date = self._get_last_day_beginning(end_date)
        else:
            end_date = self.ui.endDateTimeEdit.dateTime().toPyDateTime()
            start_date = self.ui.startDateTimeEdit.dateTime().toPyDateTime()

        self.last_matched_events = self.analyzer.analyze(
            start_date,
            end_date,
            self.ui.disableDateRange.isChecked()
        )
        chart_data = get_pie_chart(self.last_matched_events)
        self.chart.draw(chart_data)
        self._run_projects(chart_data)

    def _update_project_events(self) -> None:
        self.ui.projectEventsList.clear()
        selected_items: WidgetItems = self.ui.projectsTimesList.selectedItems()
        if len(selected_items) < 1:
            return
        if len(self.last_matched_events) < 1:
            return
        selected_project = selected_items[0].data(Qt.UserRole)
        i = 0
        items = []
        items_duration: Dict[str, float] = {}
        selected_events: List[MatchedEvent] = []

        for event in reversed(self.last_matched_events):
            if event.project == selected_project:
                data_hash = event.stringify_data()
                if data_hash not in items_duration:
                    items_duration[data_hash] = 0
                    selected_events.append(event)
                items_duration[data_hash] += event.duration.total_seconds()

        for event in selected_events:
            text = ', '.join(["{}={}".format(key, value)
                              for key, value
                              in event.data.items()])
            duration = int(items_duration[event.stringify_data()])
            text = '{}: {}'.format(duration, text)
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
        if project_name == self.config.projects.none_project:
            return 'None'
        else:
            return project_name
