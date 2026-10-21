from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import Signal
from app.models.automation import (
    Action,
    ActionType,
    Automation,
    Trigger,
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
        self.action_widgets = []

        self.displays = self.display_service.get_displays()

        self.setWindowTitle(
            "Edit Automation" if automation else "New Automation"
        )
        self.resize(620, 620)
        self.setMinimumSize(500, 480)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        title = QLabel(
            "Edit automation" if self.automation else "New automation"
        )
        title.setObjectName("pageTitle")
        description = QLabel(
            "Choose when this automation runs and what your display should do."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(description)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        form_content = QWidget()
        form_layout = QVBoxLayout(form_content)
        form_layout.setContentsMargins(0, 2, 6, 2)
        form_layout.setSpacing(14)

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("For example, Laptop dock connected")
        form.addRow("Name:", self.name_edit)

        self.enabled_combo = QComboBox()
        self.enabled_combo.addItem("Enabled", True)
        self.enabled_combo.addItem("Disabled", False)
        form.addRow("Status:", self.enabled_combo)
        form_layout.addLayout(form)

        trigger_label = QLabel("Trigger")
        trigger_label.setObjectName("sectionTitle")
        trigger_description = QLabel(
            "Run this automation when the selected device changes state."
        )
        trigger_description.setObjectName("mutedText")
        trigger_description.setWordWrap(True)
        form_layout.addWidget(trigger_label)
        form_layout.addWidget(trigger_description)

        trigger_group = QWidget()
        trigger_layout = QVBoxLayout(trigger_group)
        trigger_layout.setContentsMargins(0, 0, 0, 0)
        trigger_layout.setSpacing(8)

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
        trigger_layout.addWidget(QLabel("Device event"))
        trigger_layout.addWidget(self.trigger_type_combo)
        trigger_layout.addWidget(QLabel("Watch device"))
        trigger_layout.addWidget(self.trigger_device_combo)
        form_layout.addWidget(trigger_group)

        actions_label = QLabel("Actions")
        actions_label.setObjectName("sectionTitle")
        actions_description = QLabel(
            "Choose the display input to switch to."
        )
        actions_description.setObjectName("mutedText")
        actions_description.setWordWrap(True)
        form_layout.addWidget(actions_label)
        form_layout.addWidget(actions_description)

        self.actions_layout = QVBoxLayout()
        self.actions_layout.setSpacing(8)
        form_layout.addLayout(self.actions_layout)

        add_action_button = QPushButton("＋  Add action")
        add_action_button.setObjectName("secondaryButton")
        add_action_button.clicked.connect(self._add_action)
        form_layout.addWidget(add_action_button)
        form_layout.addStretch()
        scroll_area.setWidget(form_content)
        layout.addWidget(scroll_area, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save automation")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.accept)

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
                device.windows_device_id,
            )

    def _add_action(self, action=None):
        action_widget = ActionWidget(
            self.displays,
            action,
            self,
        )

        action_widget.remove_requested.connect(
            self._remove_action
        )

        self.action_widgets.append(action_widget)
        self.actions_layout.addWidget(action_widget)

    def _remove_action(self, action_widget):
        if action_widget in self.action_widgets:
            self.action_widgets.remove(action_widget)

        action_widget.deleteLater()

    def get_automation(self) -> Automation:
        actions = [
            action_widget.get_action()
            for action_widget in self.action_widgets
        ]

        return Automation(
            id=self.automation.id if self.automation else "",
            name=self.name_edit.text().strip(),
            enabled=self.enabled_combo.currentData(),
            trigger=Trigger(
                type=self.trigger_type_combo.currentData(),
                device_id=self.trigger_device_combo.currentData(),
            ),
            actions=actions,
        )

class ActionWidget(QWidget):

    remove_requested = Signal(object)

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
        self.setObjectName("actionEditorCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.addWidget(QLabel("Action"), 1)
        remove_button = QPushButton("Remove")
        remove_button.setObjectName("dangerButton")
        remove_button.clicked.connect(
            lambda: self.remove_requested.emit(self)
        )
        header.addWidget(remove_button)
        layout.addLayout(header)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

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

        for label_text, combo in (
            ("Action type", self.type_combo),
            ("Display", self.display_combo),
            ("Target input", self.input_combo),
        ):
            control = QWidget()
            control_layout = QVBoxLayout(control)
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_layout.setSpacing(4)
            control_layout.addWidget(QLabel(label_text))
            control_layout.addWidget(combo)
            controls_layout.addWidget(control, 1)
        layout.addLayout(controls_layout)

        self.display_combo.currentIndexChanged.connect(
            self._load_inputs
        )
        self.type_combo.currentIndexChanged.connect(
            self._update_controls
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
        self._update_controls()

    def _load_inputs(self):
        self.input_combo.clear()

        display_id = self.display_combo.currentData()

        if display_id is None:
            self._update_controls()
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
            self._update_controls()
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

        self._update_controls()

    def _update_controls(self):
        is_switch_action = (
            self.type_combo.currentData() == ActionType.SWITCH_INPUT
        )
        self.display_combo.setEnabled(
            is_switch_action and bool(self.displays)
        )
        self.input_combo.setEnabled(
            is_switch_action and self.input_combo.count() > 0
        )

    def get_action(self) -> Action:
        return Action(
            type=self.type_combo.currentData(),
            display_id=self.display_combo.currentData(),
            input_id=self.input_combo.currentData(),
        )