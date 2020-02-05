from typing import Callable, List

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from config import Project, Rule
from gui.rule_widget import RuleWidget
from .ui.project import Ui_ProjectFrame


class ProjectWidget(QtWidgets.QFrame):
    def __init__(
            self,
            project: Project,
            on_remove_rule: Callable[['ProjectWidget'], None],
            on_edit_project_name: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.ui = Ui_ProjectFrame()
        self.ui.setupUi(self)
        self.ui.nameEdit.setText(project.name)
        self._setup_rules(project)

        self.ui.removeButton.clicked.connect(
            lambda: on_remove_rule(self)
        )
        self.ui.nameEdit.textChanged.connect(on_edit_project_name)

    def _setup_rules(self, project: Project) -> None:
        layout: QVBoxLayout = self.ui.rulesBox.layout()
        for rule in project.rules:
            rule_widget = self._create_rule_widget(layout, rule)
            layout.addWidget(rule_widget)

    def _create_rule_widget(self,
                            layout: QVBoxLayout,
                            rule: Rule
                            ) -> RuleWidget:
        rule_widget = RuleWidget(rule)
        rule_widget.register_callbacks(
            lambda: layout.insertWidget(
                layout.indexOf(rule_widget),
                self._create_rule_widget(layout, Rule({"type": "app"}))
            ),
            lambda: rule_widget.remove_from(layout)
        )

        return rule_widget

    def remove_from(self, layout: QVBoxLayout) -> None:
        self.hide()
        layout.removeWidget(self)
        self.deleteLater()

    @property
    def project(self) -> Project:
        name = self.ui.nameEdit.text()
        layout: QVBoxLayout = self.ui.rulesBox.layout()
        rule_widgets: List[RuleWidget] = []
        for i in range(0, layout.count()):
            widget = layout.itemAt(i).widget()
            assert isinstance(widget, RuleWidget)
            rule_widgets.append(widget)
        return Project(name, [rule_widget.rule
                              for rule_widget
                              in rule_widgets])
