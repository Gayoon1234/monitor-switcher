from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QPushButton,
)

from app.ui.widgets.automations_card import AutomationCard
from app.ui.widgets.automation_editor import AutomationEditor


class AutomationsPage(QWidget):

    def __init__(
        self,
        repository,
        display_service,
        usb_service,
    ):
        super().__init__()

        self.repository = repository
        self.display_service = display_service
        self.usb_service = usb_service

        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)

        title = QLabel("Automations")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        self.layout.addWidget(title)

        add_button = QPushButton("Add Automation")
        add_button.clicked.connect(self._add_automation)
        self.layout.addWidget(add_button)

        self.automations_layout = QVBoxLayout()
        self.layout.addLayout(self.automations_layout)

        self._refresh_automations()

        self.layout.addStretch()

    def _refresh_automations(self):
        while self.automations_layout.count():
            item = self.automations_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        automations = self.repository.load_automations()

        if not automations:
            self.automations_layout.addWidget(
                QLabel("No automations configured.")
            )
            return

        for automation in automations:
            card = AutomationCard(
                automation,
                self.display_service,
                self.usb_service,
            )

            card.edit_requested.connect(
                self._edit_automation
            )

            card.delete_requested.connect(
                self._delete_automation
            )

            self.automations_layout.addWidget(card)

    def _edit_automation(self, automation):
        editor = AutomationEditor(
            self.display_service,
            self.usb_service,
            automation,
            self,
        )

        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        updated_automation = editor.get_automation()

        automations = self.repository.load_automations()

        for index, existing_automation in enumerate(automations):
            if existing_automation.id == updated_automation.id:
                automations[index] = updated_automation
                break

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _delete_automation(self, automation):
        result = QMessageBox.question(
            self,
            "Delete Automation",
            f"Are you sure you want to delete '{automation.name}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        automations = self.repository.load_automations()

        automations = [
            existing_automation
            for existing_automation in automations
            if existing_automation.id != automation.id
        ]

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _add_automation(self):
        editor = AutomationEditor(
            self.display_service,
            self.usb_service,
            parent=self,
        )

        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        automation = editor.get_automation()

        automations = self.repository.load_automations()

        automation.id = self._get_next_automation_id(
            automations
        )

        automations.append(automation)

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _get_next_automation_id(self, automations):
        existing_ids = {
            automation.id
            for automation in automations
        }

        index = 1

        while f"automation-{index:03d}" in existing_ids:
            index += 1

        return f"automation-{index:03d}"