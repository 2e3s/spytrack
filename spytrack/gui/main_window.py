from typing import List
from PyQt5 import QtWidgets
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QListWidgetItem, QVBoxLayout
from analyze.matched_event import MatchedEvent
from gui.main_page_widget import MainPageWidget
from gui.ui.main import Ui_Main
from config import ConfigStorage
from runner import Runner

WidgetItems = List[QListWidgetItem]


class MainWindow(QtWidgets.QMainWindow):
    ui: Ui_Main
    last_matched_events: List[MatchedEvent]

    def __init__(self,
                 config_storage: ConfigStorage,
                 stats_runner: Runner
                 ) -> None:
        super().__init__()
        self.stats_runner = stats_runner
        self.config = config_storage.load()
        self.config_storage = config_storage
        self.ui = Ui_Main()
        self.ui.setupUi(self)

        self.last_matched_events = []

        self._setup_main_widget()

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        self.hide()

    def _setup_main_widget(self) -> None:
        self.main_page_widget = MainPageWidget(
            self.config_storage,
            self.stats_runner.reload
        )
        layout: QVBoxLayout = self.ui.tabChart.layout()
        layout.addWidget(self.main_page_widget)
