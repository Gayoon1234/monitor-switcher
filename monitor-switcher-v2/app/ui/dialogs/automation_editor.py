from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
    TriggerType,
)

from PySide6.QtCore import Signal


class AutomationEditor(QDialog):

    def __init__(
        self,
        automation,
        displays,
        devices,
        parent=None,
    ):
        super().__init__(parent)

        self.automation = automation
        self.displays = displays
        self.devices = devices
        self.action_rows = []

        self.setWindowTitle(
            "Edit Automation"
            if automation
            else "Add Automation"
        )

        self.resize(500, 500)

        self._setup_ui()

        if automation:
            self._load_automation(automation)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_input = QLineEdit()
        form.addRow("Name", self.name_input)

        self.enabled_input = QComboBox()
        self.enabled_input.addItem("Enabled", True)
        self.enabled_input.addItem("Disabled", False)
        form.addRow("Status", self.enabled_input)

        self.device_input = QComboBox()

        for device in self.devices:
            self.device_input.addItem(
                device.nickname,
                device.id,
            )

        form.addRow("Device", self.device_input)

        self.trigger_input = QComboBox()
        self.trigger_input.addItem(
            "Device connects",
            TriggerType.DEVICE_CONNECTED,
        )
        self.trigger_input.addItem(
            "Device disconnects",
            TriggerType.DEVICE_DISCONNECTED,
        )

        form.addRow("When", self.trigger_input)

        layout.addLayout(form)

        layout.addWidget(QLabel("Actions"))

        self.actions_layout = QVBoxLayout()
        layout.addLayout(self.actions_layout)

        add_action_button = QPushButton("Add Action")
        add_action_button.clicked.connect(self._add_action)
        layout.addWidget(add_action_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self._add_action()

    def _add_action(self, action=None):
        row = ActionRow(
            self.displays,
            action,
        )

        row.remove_requested.connect(
            lambda: self._remove_action(row)
        )

        self.action_rows.append(row)
        self.actions_layout.addWidget(row)

    def _remove_action(self, row):
        self.action_rows.remove(row)
        row.deleteLater()

    def _load_automation(self, automation):
        self.name_input.setText(automation.name)

        enabled_index = self.enabled_input.findData(
            automation.enabled
        )
        if enabled_index >= 0:
            self.enabled_input.setCurrentIndex(enabled_index)

        trigger_device_index = self.device_input.findData(
            automation.trigger.device_id
        )
        if trigger_device_index >= 0:
            self.device_input.setCurrentIndex(
                trigger_device_index
            )

        trigger_index = self.trigger_input.findData(
            automation.trigger.type
        )
        if trigger_index >= 0:
            self.trigger_input.setCurrentIndex(
                trigger_index
            )

        for row in self.action_rows:
            row.deleteLater()

        self.action_rows.clear()

        for action in automation.actions:
            self._add_action(action)

    def get_automation(self) -> Automation:
        actions = [
            row.get_action()
            for row in self.action_rows
        ]

        if self.automation:
            automation_id = self.automation.id
        else:
            automation_id = ""

        return Automation(
            id=automation_id,
            name=self.name_input.text().strip(),
            enabled=self.enabled_input.currentData(),
            trigger=Trigger(
                type=self.trigger_input.currentData(),
                device_id=self.device_input.currentData(),
            ),
            actions=actions,
        )


class ActionRow(QWidget):

    remove_requested = Signal()

    def __init__(self, displays, action=None):
        super().__init__()

        self.displays = displays

        layout = QHBoxLayout(self)

        self.display_input = QComboBox()

        for display in displays:
            self.display_input.addItem(
                display.name,
                display.id,
            )

        self.input_input = QComboBox()

        self.display_input.currentIndexChanged.connect(
            self._update_inputs
        )

        layout.addWidget(self.display_input)
        layout.addWidget(self.input_input)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(
            self.remove_requested.emit
        )

        layout.addWidget(remove_button)

        if action:
            display_index = self.display_input.findData(
                action.display_id
            )

            if display_index >= 0:
                self.display_input.setCurrentIndex(
                    display_index
                )

            self._update_inputs()

            input_index = self.input_input.findData(
                action.input_id
            )

            if input_index >= 0:
                self.input_input.setCurrentIndex(
                    input_index
                )
        else:
            self._update_inputs()

    def _update_inputs(self):
        display = self.display_input.currentData()

        self.input_input.clear()

        for item in self.displays:
            if item.id != display:
                continue

            for input_ in item.inputs:
                self.input_input.addItem(
                    input_.input_id,
                    input_.input_id,
                )

            break

    def get_action(self) -> Action:
        return Action(
            type=ActionType.SWITCH_INPUT,
            display_id=self.display_input.currentData(),
            input_id=self.input_input.currentData(),
        )