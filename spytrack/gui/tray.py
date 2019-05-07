from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QAction, qApp, QMenu, QSystemTrayIcon
from config import ConfigStorage
from gui.main_window import MainWindow
from runner import Runner


class Tray(QSystemTrayIcon):  # type: ignore
    def __init__(self, parent: QtCore.QObject, config_storage: ConfigStorage, stats_runner: Runner) -> None:
        super(Tray, self).__init__(parent)

        self.main_window = MainWindow(config_storage, stats_runner)
        self.setIcon(self.main_window.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))

        show_action = QAction("Show/Hide", self.main_window)
        show_action.triggered.connect(self.show_hide_main_window)
        quit_action = QAction("Exit", parent)
        quit_action.triggered.connect(qApp.quit)
        self.tray_menu = QMenu()
        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(quit_action)
        self.setContextMenu(self.tray_menu)
        self.activated.connect(self.left_click)

    def left_click(self, reason: int) -> None:
        print("onTrayIconActivated:", reason)
        if reason == QSystemTrayIcon.Trigger:
            self.show_hide_main_window()

    def show_hide_main_window(self) -> None:
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
