from typing import Callable, List

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from config import Project, Rule
from gui.rule_widget import RuleWidget
from .ui.project import Ui_ProjectFrame


class ProjectWidget(QtWidgets.QFrame):  # type: ignore
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.ui = Ui_ProjectFrame()
        self.ui.setupUi(self)  # type: ignore
        self.ui.nameEdit.setText(project.name)
        self._setup_rules(project)

    def _setup_rules(self, project: Project) -> None:
        layout: QVBoxLayout = self.ui.rulesBox.layout()
        for rule in project.rules:
            rule_widget = self._create_rule_widget(layout, rule)
            layout.addWidget(rule_widget)

    def _create_rule_widget(self, layout: QVBoxLayout, rule: Rule) -> RuleWidget:
        rule_widget = RuleWidget(rule)
        rule_widget.register_callbacks(
            lambda: layout.insertWidget(  # type: ignore
                layout.indexOf(rule_widget),
                self._create_rule_widget(layout, Rule({"type": "app"}))
            ),
            lambda: rule_widget.remove_from(layout)
        )

        return rule_widget

    def register_callbacks(self, add_rule: Callable[[], None], remove_rule: Callable[[], None]) -> None:
        self.ui.addButton.clicked.connect(add_rule)
        self.ui.removeButton.clicked.connect(remove_rule)

    def remove_from(self, layout: QVBoxLayout) -> None:
        self.hide()
        self.setParent(None)
        layout.removeWidget(self)

    @property
    def project(self) -> Project:
        name = self.ui.nameEdit.text()
        layout: QVBoxLayout = self.ui.rulesBox.layout()
        rule_widgets: List[RuleWidget] = [layout.itemAt(i).widget() for i in range(0, layout.count())]
        return Project(name, [rule_widget.rule for rule_widget in rule_widgets])
