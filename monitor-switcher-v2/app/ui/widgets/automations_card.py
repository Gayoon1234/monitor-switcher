from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.models.automation import (
    ActionType,
    TriggerType,
)
class AutomationCard(QFrame):

    edit_requested = Signal(object)
    delete_requested = Signal(object)

    def __init__(
        self,
        automation,
        display_service,
        usb_service,
    ):
        super().__init__()

        self.automation = automation
        self.display_service = display_service
        self.usb_service = usb_service

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Name
        name = QLabel(self.automation.name)
        name.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        # Status
        status = QLabel(
            "Enabled" if self.automation.enabled else "Disabled"
        )

        # Trigger
        trigger = self.automation.trigger

        if trigger.type == TriggerType.DEVICE_CONNECTED:
            trigger_text = "Device connects"
        elif trigger.type == TriggerType.DEVICE_DISCONNECTED:
            trigger_text = "Device disconnects"
        else:
            trigger_text = trigger.type.value

        trigger_label = QLabel(
            f"WHEN  {trigger_text}"
        )

        # Actions
        actions_label = QLabel("DO")

        layout.addWidget(name)
        layout.addWidget(status)
        layout.addWidget(trigger_label)
        layout.addWidget(actions_label)

        for action in self.automation.actions:
            if action.type == ActionType.SWITCH_INPUT:
                action_text = (
                    f"{action.display_id} → {action.input_id}"
                )
            elif action.type == ActionType.DO_NOTHING:
                action_text = "Do nothing"
            else:
                action_text = action.type.value

            layout.addWidget(
                QLabel(f"      {action_text}")
            )

        # Buttons
        buttons_layout = QHBoxLayout()

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(
            lambda: self.edit_requested.emit(self.automation)
        )

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self.automation)
        )

        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)