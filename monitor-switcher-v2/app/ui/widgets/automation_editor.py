from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.automation import (
    ActionType,
    TriggerType,
)

class AutomationEditor(QDialog):

    def __init__(
        self,
        display_service,
        usb_service,
        automation=None,
        parent=None,
    ):
        super().__init__(parent)

        self.display_service = display_service
        self.usb_service = usb_service
        self.automation = automation

        self.displays = self.display_service.get_displays()

        self.setWindowTitle(
            "Edit Automation" if automation else "New Automation"
        )
        self.resize(500, 500)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Name
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)

        # Enabled
        self.enabled_combo = QComboBox()
        self.enabled_combo.addItem("Enabled", True)
        self.enabled_combo.addItem("Disabled", False)
        form.addRow("Status:", self.enabled_combo)

        layout.addLayout(form)

        # Trigger
        trigger_label = QLabel("WHEN")
        trigger_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(trigger_label)

        trigger_layout = QHBoxLayout()

        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItem(
            "Device connects",
            TriggerType.DEVICE_CONNECTED,
        )
        self.trigger_type_combo.addItem(
            "Device disconnects",
            TriggerType.DEVICE_DISCONNECTED,
        )

        self.trigger_device_combo = QComboBox()

        trigger_layout.addWidget(
            self.trigger_type_combo
        )
        trigger_layout.addWidget(
            self.trigger_device_combo
        )

        layout.addLayout(trigger_layout)

        # Actions
        actions_label = QLabel("DO")
        actions_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(actions_label)

        self.actions_layout = QVBoxLayout()
        layout.addLayout(self.actions_layout)

        add_action_button = QPushButton(
            "Add Action"
        )
        add_action_button.clicked.connect(
            self._add_action
        )

        layout.addWidget(add_action_button)

        layout.addStretch()

        # Dialog buttons
        buttons_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(
            self.reject
        )

        save_button = QPushButton("Save")
        save_button.clicked.connect(
            self.accept
        )

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)

    def _load_data(self):
        self._load_devices()

        if self.automation is None:
            self._add_action()
            return

        self.name_edit.setText(
            self.automation.name
        )

        enabled_index = self.enabled_combo.findData(
            self.automation.enabled
        )

        if enabled_index >= 0:
            self.enabled_combo.setCurrentIndex(
                enabled_index
            )

        trigger_index = self.trigger_type_combo.findData(
            self.automation.trigger.type
        )

        if trigger_index >= 0:
            self.trigger_type_combo.setCurrentIndex(
                trigger_index
            )

        device_index = self.trigger_device_combo.findData(
            self.automation.trigger.device_id
        )

        if device_index >= 0:
            self.trigger_device_combo.setCurrentIndex(
                device_index
            )

        for action in self.automation.actions:
            self._add_action(action)

    def _load_devices(self):
        self.trigger_device_combo.clear()

        devices = self.usb_service.get_configured_devices()

        for device in devices:
            self.trigger_device_combo.addItem(
                device.nickname,
                device.id,
            )

    def _add_action(self, action=None):
        action_widget = ActionWidget(
            self.displays,
            action,
            self,
        )

        self.actions_layout.addWidget(
            action_widget
        )


class ActionWidget(QWidget):

    def __init__(
        self,
        displays,
        action=None,
        parent=None,
    ):
        super().__init__(parent)

        self.displays = displays
        self.action = action

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        self.type_combo = QComboBox()
        self.type_combo.addItem(
            "Switch input",
            ActionType.SWITCH_INPUT,
        )
        self.type_combo.addItem(
            "Do nothing",
            ActionType.DO_NOTHING,
        )

        self.display_combo = QComboBox()
        self.input_combo = QComboBox()

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(
            self.deleteLater
        )

        layout.addWidget(self.type_combo)
        layout.addWidget(self.display_combo)
        layout.addWidget(self.input_combo)
        layout.addWidget(remove_button)

        self.display_combo.currentIndexChanged.connect(
            self._load_inputs
        )

    def _load_data(self):
        self.display_combo.clear()

        for display in self.displays:
            self.display_combo.addItem(
                display.name,
                display.id,
            )

        if self.action is not None:
            type_index = self.type_combo.findData(
                self.action.type
            )

            if type_index >= 0:
                self.type_combo.setCurrentIndex(
                    type_index
                )

            display_index = self.display_combo.findData(
                self.action.display_id
            )

            if display_index >= 0:
                self.display_combo.setCurrentIndex(
                    display_index
                )

        self._load_inputs()

    def _load_inputs(self):
        self.input_combo.clear()

        display_id = self.display_combo.currentData()

        if display_id is None:
            return

        display = next(
            (
                display
                for display in self.displays
                if display.id == display_id
            ),
            None,
        )

        if display is None:
            return

        for input_ in display.inputs:
            self.input_combo.addItem(
                input_.input_id,
                input_.input_id,
            )

        if self.action is not None:
            input_index = self.input_combo.findData(
                self.action.input_id
            )

            if input_index >= 0:
                self.input_combo.setCurrentIndex(
                    input_index
                )