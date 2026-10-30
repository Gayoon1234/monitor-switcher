from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.models.automation import ActionType, TriggerType


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
        self.setObjectName("automationCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(12)

        name = QLabel(self.automation.name or "Unnamed automation")
        name.setObjectName("cardTitle")
        name.setWordWrap(True)

        status = QLabel("Enabled" if self.automation.enabled else "Disabled")
        status.setObjectName("automationStatus")
        status.setProperty(
            "automationState",
            "enabled" if self.automation.enabled else "disabled",
        )
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(name, 1)
        header.addWidget(status, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        trigger_heading = QLabel("WHEN")
        trigger_heading.setObjectName("eyebrow")
        trigger = self.automation.trigger
        trigger_text = {
            TriggerType.DEVICE_CONNECTED: "Device connects",
            TriggerType.DEVICE_DISCONNECTED: "Device disconnects",
        }.get(trigger.type, trigger.type.value.replace("_", " ").title())
        device_name = self._device_name(trigger.device_id)
        trigger_detail = QLabel(f"{trigger_text}  ·  {device_name}")
        trigger_detail.setObjectName("automationStep")
        trigger_detail.setWordWrap(True)
        layout.addWidget(trigger_heading)
        layout.addWidget(trigger_detail)

        actions_heading = QLabel("THEN")
        actions_heading.setObjectName("eyebrow")
        layout.addWidget(actions_heading)

        display_names = {
            display.id: display.name
            for display in self.display_service.get_displays()
        }
        for action in self.automation.actions:
            if action.type == ActionType.SWITCH_INPUT:
                display_name = display_names.get(
                    action.display_id,
                    action.display_id or "Unknown display",
                )
                action_text = f"{display_name}  →  {action.input_id or 'Unknown input'}"
            elif action.type == ActionType.DO_NOTHING:
                action_text = "Do nothing"
            else:
                action_text = action.type.value.replace("_", " ").title()

            action_label = QLabel(action_text)
            action_label.setObjectName("automationStep")
            action_label.setWordWrap(True)
            layout.addWidget(action_label)

        if not self.automation.actions:
            no_actions = QLabel("No actions configured")
            no_actions.setObjectName("mutedText")
            layout.addWidget(no_actions)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(
            lambda: self.edit_requested.emit(self.automation)
        )

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self.automation)
        )

        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)

    def _device_name(self, device_id):
        for device in self.usb_service.get_configured_devices():
            if device.windows_device_id == device_id:
                return device.nickname
        return device_id or "Unknown device"
