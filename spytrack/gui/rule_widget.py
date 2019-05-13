from typing import Callable, Dict
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from config import Rule
from .ui.rule import Ui_RuleFrame


class RuleWidget(QtWidgets.QFrame):  # type: ignore
    RULE_APP = 0
    RULE_WEB = 1

    def __init__(self, rule: Rule) -> None:
        super().__init__()
        self.ui = Ui_RuleFrame()
        self.ui.setupUi(self)  # type: ignore
        self._rule = rule

        if rule.is_app():
            self.ui.typesBox.setCurrentIndex(RuleWidget.RULE_APP)
            self.ui.urlEdit.hide()
            self.ui.urlLabel.hide()
        else:
            self.ui.typesBox.setCurrentIndex(RuleWidget.RULE_WEB)

        if 'url' in rule:
            self.ui.urlEdit.setText(rule['url'])
        if 'app' in rule:
            self.ui.appEdit.setText(rule['app'])
        if 'title' in rule:
            self.ui.titleEdit.setText(rule['title'])

        self.ui.typesBox.currentIndexChanged.connect(self._type_box_changed)

    def register_callbacks(self,
                           add_rule: Callable[[], None],
                           remove_rule: Callable[[], None]
                           ) -> None:
        self.ui.addButton.clicked.connect(add_rule)
        self.ui.removeButton.clicked.connect(remove_rule)

    def _type_box_changed(self) -> None:
        if self.ui.typesBox.currentIndex() == RuleWidget.RULE_APP:
            self.ui.urlEdit.hide()
            self.ui.urlLabel.hide()
        else:
            self.ui.urlEdit.show()
            self.ui.urlLabel.show()

    def remove_from(self, layout: QVBoxLayout) -> None:
        self.hide()
        self.setParent(None)
        layout.removeWidget(self)

    @property
    def rule(self) -> Rule:
        is_app = self.ui.typesBox.currentIndex() == RuleWidget.RULE_APP
        data = {
            'id': self._rule.id,
            'type': Rule.APP if is_app else Rule.WEB
        }
        if not is_app and len(self.ui.urlEdit.text()):
            self._add_value(data, 'url', self.ui.urlEdit.text())
        self._add_value(data, 'title', self.ui.titleEdit.text())
        self._add_value(data, 'app', self.ui.appEdit.text())

        return Rule(data)

    def _add_value(self, data: Dict[str, str], key: str, value: str) -> None:
        if len(value) > 0:
            data[key] = value
