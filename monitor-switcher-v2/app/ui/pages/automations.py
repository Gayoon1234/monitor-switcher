from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.automations_card import AutomationCard

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
            layout.addWidget(
                AutomationCard(
                    automation,
                    self.display_service,
                    self.usb_service
                )
            )

        layout.addStretch()