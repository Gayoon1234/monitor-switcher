from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)
    activity_days_changed = Signal(object)
    clear_activity_requested = Signal()

    ACTIVITY_PERIODS = (
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
        ("Last 365 days", 365),
        ("All activity", None),
    )

    def __init__(self, theme_service, activity_days: int | None = 30):
        super().__init__()
        self.theme_service = theme_service

        layout = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        description = QLabel("Choose an application color theme.")
        self.theme_selector = QComboBox()
        for theme_name in self.theme_service.get_theme_names():
            self.theme_selector.addItem(theme_name.title(), theme_name)

        active_index = self.theme_selector.findData(
            self.theme_service.get_active_theme()
        )
        self.theme_selector.setCurrentIndex(active_index)
        self.theme_selector.currentIndexChanged.connect(
            self._on_theme_selected
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(QLabel("Color theme"))
        layout.addWidget(self.theme_selector)

        activity_title = QLabel("Activity history")
        activity_title.setObjectName("sectionTitle")
        activity_description = QLabel(
            "Choose how much history to show. Older events remain saved."
        )
        activity_description.setWordWrap(True)

        self.activity_period_selector = QComboBox()
        for label, days in self.ACTIVITY_PERIODS:
            self.activity_period_selector.addItem(label, days)
        period_index = self.activity_period_selector.findData(activity_days)
        if period_index < 0:
            raise ValueError(f"Unsupported activity history period: {activity_days}")
        self.activity_period_selector.setCurrentIndex(period_index)
        self.activity_period_selector.currentIndexChanged.connect(
            self._on_activity_period_selected
        )

        self.clear_activity_button = QPushButton("Delete all activity logs")
        self.clear_activity_button.setObjectName("dangerButton")
        self.clear_activity_button.clicked.connect(
            self._confirm_clear_activity
        )

        layout.addWidget(activity_title)
        layout.addWidget(activity_description)
        layout.addWidget(QLabel("Show activity from"))
        layout.addWidget(self.activity_period_selector)
        layout.addWidget(self.clear_activity_button)
        layout.addStretch()

    def _on_theme_selected(self, index: int) -> None:
        theme_name = self.theme_selector.itemData(index)
        if theme_name:
            self.theme_changed.emit(theme_name)

    def _on_activity_period_selected(self, index: int) -> None:
        self.activity_days_changed.emit(
            self.activity_period_selector.itemData(index)
        )

    def _confirm_clear_activity(self) -> None:
        result = QMessageBox.question(
            self,
            "Delete Activity Logs",
            "Permanently delete all saved activity logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            self.clear_activity_requested.emit()
