from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, theme_service):
        super().__init__()
        self.theme_service = theme_service

        layout = QVBoxLayout(self)
        title = QLabel("Settings")
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
        layout.addStretch()

    def _on_theme_selected(self, index: int) -> None:
        theme_name = self.theme_selector.itemData(index)
        if theme_name:
            self.theme_changed.emit(theme_name)
