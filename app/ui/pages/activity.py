from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ActivityItem(QFrame):
    def __init__(self, event):
        super().__init__()
        self.setObjectName("activityItem")
        self.setProperty(
            "eventState",
            "success" if event.success else "failed",
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        time_column = QVBoxLayout()
        time_column.setSpacing(2)
        date_label = QLabel(event.timestamp.strftime("%d %b %Y"))
        date_label.setObjectName("mutedText")
        time_label = QLabel(event.timestamp.strftime("%H:%M:%S"))
        time_label.setObjectName("activityTime")
        time_column.addWidget(date_label)
        time_column.addWidget(time_label)
        time_column.addStretch()

        details_column = QVBoxLayout()
        details_column.setSpacing(6)
        detail_header = QHBoxLayout()

        event_type_label = QLabel(
            event.event_type.replace("_", " ").title()
        )
        event_type_label.setObjectName("activityType")
        result_label = QLabel("Succeeded" if event.success else "Failed")
        result_label.setObjectName("activityStatus")
        result_label.setProperty(
            "eventState",
            "success" if event.success else "failed",
        )
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        detail_header.addWidget(event_type_label)
        detail_header.addStretch()
        detail_header.addWidget(result_label)

        message_label = QLabel(event.message)
        message_label.setObjectName("activityMessage")
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        details_column.addLayout(detail_header)
        details_column.addWidget(message_label)

        layout.addLayout(time_column)
        layout.addLayout(details_column, 1)


class ActivityPage(QWidget):
    PAGE_SIZE = 25

    def __init__(self, activity_history=None, days: int | None = 30):
        super().__init__()
        self.total_events = 0
        self.successful_events = 0
        self.failed_events = 0
        self.days = days
        self._events = []
        self._current_page = 0

        self._setup_ui()

        if activity_history:
            self.set_events(activity_history)

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 20, 24, 20)
        self.layout.setSpacing(12)

        title = QLabel("Activity")
        title.setObjectName("pageTitle")
        subtitle = QLabel("A history of device events and automation actions.")
        subtitle.setObjectName("mutedText")
        self.summary = QLabel("No events yet")
        self.summary.setObjectName("activitySummary")

        header = QHBoxLayout()
        heading = QVBoxLayout()
        heading.setSpacing(4)
        heading.addWidget(title)
        heading.addWidget(subtitle)
        header.addLayout(heading)
        header.addStretch()
        header.addWidget(self.summary)
        self.layout.addLayout(header)

        self.empty_state = QLabel("Events will appear here as they happen.")
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.activity_container = QVBoxLayout()
        self.activity_container.setSpacing(8)
        self.activity_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_content = QWidget()
        scroll_content.setObjectName("activityList")
        scroll_content.setLayout(self.activity_container)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("activityScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(scroll_content)

        self.activity_container.addWidget(self.empty_state)
        self.layout.addWidget(scroll_area)

        pagination = QHBoxLayout()
        self.previous_page_button = QPushButton("Previous")
        self.previous_page_button.clicked.connect(self._show_previous_page)
        self.page_label = QLabel("No pages")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_page_button = QPushButton("Next")
        self.next_page_button.clicked.connect(self._show_next_page)
        pagination.addStretch()
        pagination.addWidget(self.previous_page_button)
        pagination.addWidget(self.page_label)
        pagination.addWidget(self.next_page_button)
        pagination.addStretch()
        self.layout.addLayout(pagination)
        self._update_pagination_controls()

    def add_event(self, event):
        self._events.insert(0, event)
        self.total_events += 1
        if event.success:
            self.successful_events += 1
        else:
            self.failed_events += 1

        if self._current_page == 0:
            self._render_page()
        else:
            self._update_summary()
            self._update_pagination_controls()

    def set_events(self, events) -> None:
        self._events = list(reversed(list(events or [])))
        self._current_page = 0
        self.total_events = len(self._events)
        self.successful_events = sum(
            event.success for event in self._events
        )
        self.failed_events = self.total_events - self.successful_events
        self._render_page()

    def _render_page(self) -> None:
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            widget = item.widget()
            if widget is not None and widget is not self.empty_state:
                widget.setParent(None)
                widget.deleteLater()

        if not self._events:
            self.empty_state.show()
            self.activity_container.addWidget(self.empty_state)
            self.summary.setText("No events yet")
        else:
            self.empty_state.hide()
            start = self._current_page * self.PAGE_SIZE
            for event in self._events[start:start + self.PAGE_SIZE]:
                self.activity_container.addWidget(ActivityItem(event))
            self._update_summary()

        self._update_pagination_controls()

    def _show_previous_page(self) -> None:
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def _show_next_page(self) -> None:
        if (self._current_page + 1) * self.PAGE_SIZE < self.total_events:
            self._current_page += 1
            self._render_page()

    def _update_pagination_controls(self) -> None:
        page_count = (
            self.total_events + self.PAGE_SIZE - 1
        ) // self.PAGE_SIZE
        self.page_label.setText(
            f"Page {self._current_page + 1} of {page_count}"
            if page_count
            else "No pages"
        )
        self.previous_page_button.setEnabled(self._current_page > 0)
        self.next_page_button.setEnabled(
            self._current_page + 1 < page_count
        )

    def _update_summary(self):
        self.summary.setText(
            f"{self.total_events} events  ·  "
            f"{self.successful_events} successful  ·  "
            f"{self.failed_events} failed"
        )
