import json
import re
from pathlib import Path


class ThemeService:
    DEFAULT_COLORS = {
        "background": "#1e1e1e",
        "surface": "#252526",
        "surface_alt": "#333333",
        "text": "#f1f1f1",
        "muted_text": "#b0b0b0",
        "primary": "#4c8dff",
        "border": "#3c3c3c",
        "configured_background": "#29432f",
        "configured_border": "#4f7d59",
        "unconfigured_background": "#4a4328",
        "unconfigured_border": "#8a7a3a",
    }
    COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{6}")

    def __init__(self, path: str = "theme.json"):
        self.path = Path(path)
        self.colors = self._load_colors()

    def get_color(self, name: str) -> str:
        try:
            return self.colors[name]
        except KeyError as error:
            raise KeyError(f"Unknown theme color: {name}") from error

    def get_colors(self) -> dict[str, str]:
        return self.colors.copy()

    def get_stylesheet(self) -> str:
        colors = self.colors

        return f"""
            QWidget {{
                background-color: {colors["background"]};
                color: {colors["text"]};
            }}
            QLabel {{
                background-color: transparent;
            }}
            QMainWindow, QStackedWidget, QScrollArea {{
                background-color: {colors["background"]};
            }}
            QListWidget {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                outline: none;
            }}
            QScrollBar:vertical {{
                background-color: {colors["surface"]};
                width: 10px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors["surface_alt"]};
                min-height: 24px;
                border-radius: 4px;
                border: none;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background-color: {colors["surface"]};
                height: 10px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {colors["surface_alt"]};
                min-width: 24px;
                border-radius: 4px;
                border: none;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
                border: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
            QListWidget::item {{
                min-height: 24px;
                padding: 8px 10px;
                margin: 2px 4px;
            }}
            QListWidget::item:selected {{
                background-color: {colors["primary"]};
                color: {colors["surface"]};
            }}
            QPushButton, QLineEdit, QComboBox {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                border-color: {colors["primary"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["surface_alt"]};
            }}
            QLineEdit::placeholder {{
                color: {colors["muted_text"]};
            }}
            UsbDeviceCard[deviceState="configured"] {{
                background-color: {colors["configured_background"]};
                border: 1px solid {colors["configured_border"]};
                border-radius: 8px;
            }}
            UsbDeviceCard[deviceState="unconfigured"] {{
                background-color: {colors["unconfigured_background"]};
                border: 1px solid {colors["unconfigured_border"]};
                border-radius: 8px;
            }}
        """

    def _load_colors(self) -> dict[str, str]:
        colors = self.DEFAULT_COLORS.copy()

        if not self.path.exists():
            return colors

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Theme file must contain a JSON object.")

        overrides = data.get("colors", {})
        if not isinstance(overrides, dict):
            raise ValueError("Theme 'colors' must be a JSON object.")

        unknown_colors = overrides.keys() - colors.keys()
        if unknown_colors:
            names = ", ".join(sorted(unknown_colors))
            raise ValueError(f"Unknown theme color(s): {names}")

        for name, value in overrides.items():
            if (
                not isinstance(value, str)
                or self.COLOR_PATTERN.fullmatch(value) is None
            ):
                raise ValueError(
                    f"Theme color '{name}' must be a six-digit hex color."
                )
            colors[name] = value

        return colors
