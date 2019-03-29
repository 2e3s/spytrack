from PyQt5 import QtWidgets, QtCore
from gui.ui import main
from config import ConfigStorage
from runner import Runner


class MainWindow(QtWidgets.QMainWindow):
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
        pass

    def _run_timer(self) -> None:
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run_chart)
        self.timer.start(self.config.get_interval() * 5000)

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
