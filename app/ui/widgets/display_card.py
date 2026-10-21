from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QFrame,
    QVBoxLayout,
)


class DisplayCard(QFrame):

    def __init__(self, display, display_service):
        super().__init__()

        self.display = display
        self.display_service = display_service

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.setObjectName("displayCard")

        self.name = QLabel(self.display.name)
        self.name.setObjectName("cardTitle")
        self.name.setWordWrap(True)

        self.status = QLabel("Connected")
        self.status.setObjectName("deviceStatus")
        self.status.setProperty("connectionState", "connected")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header = QHBoxLayout()
        header.addWidget(self.name, 1)
        header.addWidget(self.status)

        self.current_input = QLabel(
            f"Current input: {self.display.current_input or 'Unknown'}"
        )
        self.current_input.setObjectName("mutedText")

        self.input_selector = QComboBox()

        for display_input in self.display.inputs:
            self.input_selector.addItem(display_input.input_id)

        if self.display.current_input:
            index = self.input_selector.findText(
                self.display.current_input
            )

            if index >= 0:
                self.input_selector.setCurrentIndex(index)

        self.input_selector.setEnabled(bool(self.display.inputs))
        self.input_selector.setToolTip(
            "Select the monitor input to switch to."
        )
        self.input_selector.currentTextChanged.connect(
            self._switch_input
        )

        layout.addLayout(header)
        layout.addWidget(self.current_input)
        layout.addWidget(QLabel("Switch input"))
        layout.addWidget(self.input_selector)

    def _switch_input(self, input_id):
        if input_id == self.display.current_input:
            return

        self.display_service.switch_input(
            self.display.id,
            input_id,
        )

        self.display.current_input = input_id

        self.current_input.setText(
            f"Current input: {input_id}"
        )