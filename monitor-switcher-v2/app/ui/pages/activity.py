from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ActivityItem(QFrame):

    def __init__(self, event):
        super().__init__()

        layout = QHBoxLayout(self)

        time_label = QLabel(
            event.timestamp.strftime("%d/%m/%Y %H:%M:%S")
        )

        status_label = QLabel(
            "✓" if event.success else "✕"
        )

        message_label = QLabel(event.message)

        layout.addWidget(time_label)
        layout.addWidget(status_label)
        layout.addWidget(message_label)

        layout.addStretch()


class ActivityPage(QWidget):

    def __init__(self, activity_history=None):
        super().__init__()

        self._setup_ui()

        if activity_history:
            for event in activity_history:
                self.add_event(event)

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)

        title = QLabel("Activity")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        self.activity_container = QVBoxLayout()

        scroll_content = QWidget()
        scroll_content.setLayout(self.activity_container)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)

        self.layout.addWidget(scroll_area)

    def add_event(self, event):
        item = ActivityItem(event)

        self.activity_container.insertWidget(
            0,
            item,
        )