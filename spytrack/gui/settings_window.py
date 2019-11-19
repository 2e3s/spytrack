from typing import List, Callable

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout

from config import Project, Rule, Projects, Config
from gui.project_widget import ProjectWidget
from gui.ui.settings import Ui_settingsWindow
from config import ConfigStorage


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self,
                 config: Config,
                 config_storage: ConfigStorage,
                 reload_config: Callable[[Config], None]) -> None:
        super().__init__()
        self.reload_config = reload_config
        self.config = config
        self.config_storage = config_storage
        self.ui = Ui_settingsWindow()
        self.ui.setupUi(self)

        self._setup_projects_settings()
        self._setup_server_settings()

    def accept(self) -> None:
        self._modify_config()

        super().accept()

    def _get_projects(self) -> List[Project]:
        layout: QVBoxLayout = self.ui.projectsBox.layout()
        widgets: List[ProjectWidget] = [layout.itemAt(i).widget()
                                        for i
                                        in range(0, layout.count())]
        return [widget.project for widget in widgets]

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

    def _modify_config(self) -> None:
        self.config.port = int(self.ui.portBox.value())
        self.config.host = self.ui.hostEdit.text()
        self.config.interval = int(self.ui.intervalBox.value())
        self.config.run_daemon = self.ui.isLocalServerBox.isChecked()
        self.config.projects = Projects(
            self._get_projects(),
            self.config.projects.none_project
        )

        self.config_storage.save(self.config)
        self.reload_config(self.config)
