from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)
    activity_days_changed = Signal(object)
    clear_activity_requested = Signal()
    activity_logging_paused_changed = Signal(bool)
    usb_monitor_enabled_changed = Signal(bool)
    usb_monitor_interval_changed = Signal(int)

    ACTIVITY_PERIODS = (
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
        ("Last 365 days", 365),
        ("All activity", None),
    )

    def __init__(
        self,
        theme_service,
        activity_days: int | None = 30,
        activity_logging_paused: bool = False,
        usb_monitor_enabled: bool = True,
        usb_monitor_interval_ms: int = 500,
    ):
        super().__init__()
        self.theme_service = theme_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

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

        theme_section, theme_layout = self._create_section("Color theme")
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Application theme"))
        theme_row.addWidget(self.theme_selector, 1)
        theme_layout.addLayout(theme_row)

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

        self.activity_logging_button = QPushButton()
        self.activity_logging_button.setCheckable(True)
        self.activity_logging_button.setChecked(activity_logging_paused)
        self._update_activity_logging_button(activity_logging_paused)
        self.activity_logging_button.toggled.connect(
            self._on_activity_logging_toggled
        )

        self.clear_activity_button = QPushButton("Delete all activity logs")
        self.clear_activity_button.setObjectName("dangerButton")
        self.clear_activity_button.clicked.connect(
            self._confirm_clear_activity
        )

        activity_section, activity_layout = self._create_section(
            "Activity history"
        )
        self.activity_filter_row = QHBoxLayout()
        self.activity_filter_row.addWidget(QLabel("Show activity from:"))
        self.activity_filter_row.addWidget(
            self.activity_period_selector,
            1,
        )
        activity_layout.addLayout(self.activity_filter_row)

        self.activity_actions_row = QHBoxLayout()
        self.activity_actions_row.addWidget(
            self.activity_logging_button,
            1,
        )
        self.activity_actions_row.addWidget(
            self.clear_activity_button,
            1,
        )

        activity_layout.addLayout(self.activity_actions_row)

        usb_monitor_section, usb_monitor_layout = self._create_section(
            "USB device monitoring"
        )
        self.usb_monitor_button = QPushButton()
        self.usb_monitor_button.setCheckable(True)
        self.usb_monitor_button.setChecked(usb_monitor_enabled)
        self._update_usb_monitor_button(usb_monitor_enabled)
        self.usb_monitor_button.toggled.connect(
            self._on_usb_monitor_toggled
        )
        usb_monitor_layout.addWidget(self.usb_monitor_button)

        self.usb_monitor_interval_spinbox = QSpinBox()
        self.usb_monitor_interval_spinbox.setRange(1, 2_147_483_647)
        self.usb_monitor_interval_spinbox.setSuffix(" ms")
        self.usb_monitor_interval_spinbox.setValue(
            usb_monitor_interval_ms
        )
        self.usb_monitor_interval_spinbox.valueChanged.connect(
            self.usb_monitor_interval_changed.emit
        )
        usb_monitor_interval_row = QHBoxLayout()
        usb_monitor_interval_row.addWidget(
            QLabel("Polling interval:")
        )
        usb_monitor_interval_row.addWidget(
            self.usb_monitor_interval_spinbox,
            1,
        )
        usb_monitor_layout.addLayout(usb_monitor_interval_row)

        layout.addWidget(title)
        layout.addWidget(theme_section)
        layout.addWidget(activity_section)
        layout.addWidget(usb_monitor_section)
        layout.addStretch()

    def _create_section(self, title: str):
        section = QFrame()
        section.setObjectName("settingsSectionCard")

        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(18, 16, 18, 16)
        section_layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        section_layout.addWidget(heading)

        return section, section_layout

    def _on_theme_selected(self, index: int) -> None:
        theme_name = self.theme_selector.itemData(index)
        if theme_name:
            self.theme_changed.emit(theme_name)

    def _on_activity_period_selected(self, index: int) -> None:
        self.activity_days_changed.emit(
            self.activity_period_selector.itemData(index)
        )

    def _on_activity_logging_toggled(self, paused: bool) -> None:
        self._update_activity_logging_button(paused)
        self.activity_logging_paused_changed.emit(paused)

    def _update_activity_logging_button(self, paused: bool) -> None:
        self.activity_logging_button.setText(
            "Click to start recording Activity Logs"
            if paused
            else "Click to pause Activity Logs"
        )

    def _on_usb_monitor_toggled(self, enabled: bool) -> None:
        self._update_usb_monitor_button(enabled)
        self.usb_monitor_enabled_changed.emit(enabled)

    def _update_usb_monitor_button(self, enabled: bool) -> None:
        self.usb_monitor_button.setText(
            "Click to stop USB device monitoring"
            if enabled
            else "Click to start USB device monitoring"
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
