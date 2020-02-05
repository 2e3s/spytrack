from typing import List, Callable

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QToolBox

from config import Project, Rule, Config
from gui.project_widget import ProjectWidget
from gui.ui.settings import Ui_settingsWindow
from config import ConfigStorage


class SettingsWindow(QtWidgets.QDialog):
    config: Config

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

        self.actual_project_widgets: List[ProjectWidget] = []
        self._setup_projects_settings()
        self._setup_server_settings()

    def accept(self) -> None:
        self._modify_config()

        super().accept()

    def _get_projects(self) -> List[Project]:
        return [widget.project for widget in self.actual_project_widgets]

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
        self.ui.addProjectButton.clicked.connect(self._add_callback)
        layout: QVBoxLayout = self.ui.projectsFrame.layout()

        self.projects_box: QToolBox = QToolBox()
        self.projects_box.setFrameShape(QFrame.NoFrame)
        self.projects_box.setLineWidth(0)
        self.projects_box.setFrameShadow(QFrame.Plain)

        layout.addWidget(self.projects_box)
        for project in self.config.projects:
            if project.name == self.config.projects.none_project:
                continue
            project_widget = self._create_project_widget(project)
            self.projects_box.addItem(project_widget, project.name)

    def _create_project_widget(self, project: Project) -> ProjectWidget:
        project_widget = ProjectWidget(project, self._remove_callback)
        self.actual_project_widgets.append(project_widget)

        return project_widget

    def _add_callback(self) -> None:
        new_project_name = 'New project'
        empty_project = Project(new_project_name, [Rule({'type': 'app'})])
        project_widget = self._create_project_widget(empty_project)
        self.projects_box.addItem(project_widget, new_project_name)
        self.projects_box.setCurrentWidget(project_widget)

    def _remove_callback(self, project_widget: ProjectWidget) -> None:
        self.actual_project_widgets.remove(project_widget)
        project_widget.remove_from(self.ui.projectsFrame.layout())

    def _modify_config(self) -> None:
        self.config = self.config.modify(
            int(self.ui.portBox.value()),
            self.ui.hostEdit.text(),
            int(self.ui.intervalBox.value()),
            self.ui.isLocalServerBox.isChecked(),
            self._get_projects()
        )

        self.config_storage.save(self.config)
        self.reload_config(self.config)
