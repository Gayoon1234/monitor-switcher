from PySide6.QtWidgets import (
    QComboBox,
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

        self.name = QLabel(self.display.name)
        self.name.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        self.status = QLabel("Connected")

        self.current_input = QLabel(
            f"Current input: {self.display.current_input}"
        )

        self.input_selector = QComboBox()

        for input in self.display.inputs:
            self.input_selector.addItem(input.input_id)

        if self.display.current_input:
            index = self.input_selector.findText(
                self.display.current_input
            )

            if index >= 0:
                self.input_selector.setCurrentIndex(index)

        self.input_selector.currentTextChanged.connect(
            self._switch_input
        )

        layout.addWidget(self.name)
        layout.addWidget(self.status)
        layout.addWidget(self.current_input)
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