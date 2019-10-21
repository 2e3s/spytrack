from typing import List
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QListWidgetItem, QVBoxLayout
from analyze.matched_event import MatchedEvent
from gui.main_page_widget import MainPageWidget
from gui.project_widget import ProjectWidget
from gui.ui.main import Ui_Main
from config import ConfigStorage, Project, Rule, Projects
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
        self.ui.setupUi(self)  # type: ignore

        self.last_matched_events = []

        self._setup_projects_settings()
        self._setup_server_settings()
        self._setup_main_widget()

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        self.hide()

    def _setup_main_widget(self) -> None:
        self.main_page_widget = MainPageWidget(self.config)
        layout: QVBoxLayout = self.ui.tabChart.layout()
        layout.addWidget(self.main_page_widget)

    def _setup_server_settings(self) -> None:
        self.ui.portBox.setValue(self.config.port)
        self.ui.intervalBox.setValue(self.config.interval)
        self.ui.hostEdit.setText(self.config.host)

        def _state_changed() -> None:
            self.ui.hostEdit.setDisabled(self.ui.isLocalServerBox.isChecked())

        self.ui.isLocalServerBox.stateChanged.connect(_state_changed)
        self.ui.isLocalServerBox.setCheckState(QtCore.Qt.Checked
                                               if self.config.run_daemon
                                               else QtCore.Qt.Unchecked)
        self.ui.applyButton.clicked.connect(self._modify_config)

    def _setup_projects_settings(self) -> None:
        layout: QVBoxLayout = self.ui.projectsBox.layout()
        for project in self.config.projects:
            if project.name == self.config.projects.none_project:
                continue
            project_widget = self._create_project_widget(layout, project)
            layout.addWidget(project_widget)

    def _create_project_widget(self,
                               layout: QVBoxLayout,
                               project: Project) -> ProjectWidget:
        project_widget = ProjectWidget(project)
        project_widget.register_callbacks(
            lambda: layout.insertWidget(
                layout.indexOf(project_widget),
                self._create_project_widget(layout,
                                            Project('',
                                                    [Rule({'type': 'app'})]
                                                    )
                                            )
            ),
            lambda: project_widget.remove_from(layout)
        )
        return project_widget

    def _get_projects(self) -> List[Project]:
        layout: QVBoxLayout = self.ui.projectsBox.layout()
        widgets: List[ProjectWidget] = [layout.itemAt(i).widget()
                                        for i
                                        in range(0, layout.count())]
        return [widget.project for widget in widgets]

    def _modify_config(self) -> None:
        self.ui.applyButton.setDisabled(True)

        self.config.port = int(self.ui.portBox.value())
        self.config.host = self.ui.hostEdit.text()
        self.config.interval = int(self.ui.intervalBox.value())
        self.config.run_daemon = self.ui.isLocalServerBox.isChecked()
        self.config.projects = Projects(
            self._get_projects(),
            self.config.projects.none_project
        )

        self.config_storage.save(self.config)
        self.stats_runner.reload(self.config)
        self.main_page_widget.reload_config(self.config)
        self.ui.applyButton.setDisabled(False)
