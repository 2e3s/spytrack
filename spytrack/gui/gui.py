import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from config import ConfigStorage
from runner import Runner
from .tray import Tray
from .main_window import MainWindow


class Gui:
    timer: QtCore.QTimer

    def __init__(self,
                 config_storage: ConfigStorage,
                 stats_runner: Runner
                 ) -> None:
        self.stats_runner = stats_runner
        self.config_storage = config_storage

    def run(self) -> None:
        app = QtWidgets.QApplication(sys.argv)
        with self.stats_runner:
            main_window = MainWindow(self.config_storage, self.stats_runner)
            tray_icon = Tray(app, main_window)
            tray_icon.show()
            exit_code = app.exec_()
        sys.exit(exit_code)

    def run_headless(self) -> None:
        app = QtWidgets.QApplication(sys.argv)
        with self.stats_runner:
            tray_icon = Tray(app)
            tray_icon.show()
            exit_code = app.exec_()
        sys.exit(exit_code)
