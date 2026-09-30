from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
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
        layout = QVBoxLayout(self)

        title = QLabel("Automations")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(title)

        automations = self.repository.load_automations()

        if not automations:
            layout.addWidget(
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

            layout.addWidget(card)

        layout.addStretch()

    def _edit_automation(self, automation):
        editor = AutomationEditor(
            self.display_service,
            self.usb_service,
            automation,
            self,
        )

        editor.exec()


    def _delete_automation(self, automation):
        print("Delete:", automation.id)