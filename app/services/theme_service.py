import json
import re
from pathlib import Path


class ThemeService:
    DEFAULT_THEMES = {
        "dark": {
            "background": "#1e1e1e",
            "surface": "#252526",
            "surface_alt": "#333333",
            "text": "#f1f1f1",
            "muted_text": "#b0b0b0",
            "primary": "#4c8dff",
            "primary_text": "#ffffff",
            "border": "#3c3c3c",
            "configured_background": "#29432f",
            "configured_border": "#4f7d59",
            "unconfigured_background": "#4a4328",
            "unconfigured_border": "#8a7a3a",
        },
        "light": {
            "background": "#f4f5f7",
            "surface": "#ffffff",
            "surface_alt": "#f3f4f6",
            "text": "#202124",
            "muted_text": "#5f6368",
            "primary": "#2563eb",
            "primary_text": "#ffffff",
            "border": "#d1d5db",
            "configured_background": "#e8f5e9",
            "configured_border": "#81c784",
            "unconfigured_background": "#fff8e1",
            "unconfigured_border": "#ffca28",
        },
        "hacker": {
            "background": "#000000",
            "surface": "#080d08",
            "surface_alt": "#142014",
            "text": "#39ff14",
            "muted_text": "#20b510",
            "primary": "#00ff41",
            "primary_text": "#000000",
            "border": "#145214",
            "configured_background": "#08210a",
            "configured_border": "#00cc33",
            "unconfigured_background": "#101c08",
            "unconfigured_border": "#67ff00",
        },
        "harlequin": {
            "background": "#fff2b2",
            "surface": "#bde0fe",
            "surface_alt": "#ffd6a5",
            "text": "#24123a",
            "muted_text": "#493a59",
            "primary": "#7209b7",
            "primary_text": "#ffffff",
            "border": "#1d3557",
            "configured_background": "#b7ef8a",
            "configured_border": "#287a2a",
            "unconfigured_background": "#ffadad",
            "unconfigured_border": "#a61b45",
        },
    }
    DEFAULT_COLORS = DEFAULT_THEMES["dark"]
    COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{6}")

    def __init__(self, path: str = "theme.json"):
        self.path = Path(path)
        self.themes = {
            name: colors.copy()
            for name, colors in self.DEFAULT_THEMES.items()
        }
        self.active_theme = "dark"

        if self.path.exists():
            self._load_theme_file()

    def get_color(self, name: str) -> str:
        try:
            return self.themes[self.active_theme][name]
        except KeyError as error:
            raise KeyError(f"Unknown theme color: {name}") from error

    def get_colors(self) -> dict[str, str]:
        return self.themes[self.active_theme].copy()

    def get_theme_names(self) -> list[str]:
        return list(self.themes)

    def get_active_theme(self) -> str:
        return self.active_theme

    def set_active_theme(self, name: str) -> None:
        if name not in self.themes:
            raise ValueError(f"Unknown theme: {name}")

        self.active_theme = name
        self._save_theme_file()

    def get_stylesheet(self) -> str:
        colors = self.themes[self.active_theme]

        return f"""
            QWidget {{
                background-color: {colors["background"]};
                color: {colors["text"]};
            }}
            QLabel {{
                background-color: transparent;
            }}
            QLabel#pageTitle {{
                font-size: 26px;
                font-weight: 700;
            }}
            QLabel#sectionTitle, QLabel#cardTitle {{
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#mutedText, QLabel#eyebrow {{
                color: {colors["muted_text"]};
            }}
            QLabel#eyebrow {{
                font-size: 10px;
                font-weight: 700;
            }}
            QLabel#deviceStatus, QLabel#activityStatus {{
                background-color: {colors["configured_background"]};
                border: 1px solid {colors["configured_border"]};
                border-radius: 9px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel#deviceStatus[connectionState="disconnected"],
            QLabel#activityStatus[eventState="failed"] {{
                background-color: {colors["unconfigured_background"]};
                border-color: {colors["unconfigured_border"]};
            }}
            QLabel#activityTime {{
                font-size: 14px;
                font-weight: 700;
            }}
            QLabel#activityType {{
                font-size: 12px;
                font-weight: 700;
            }}
            QLabel#activityMessage {{
                font-size: 13px;
            }}
            QLabel#activitySummary {{
                color: {colors["muted_text"]};
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 10px;
                padding: 7px 10px;
            }}
            QLabel#automationSummary {{
                color: {colors["muted_text"]};
                font-size: 12px;
            }}
            QLabel#automationStep {{
                background-color: {colors["surface_alt"]};
                border-radius: 6px;
                padding: 9px 11px;
            }}
            QLabel#automationStatus {{
                background-color: {colors["configured_background"]};
                border: 1px solid {colors["configured_border"]};
                border-radius: 10px;
                padding: 4px 9px;
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel#automationStatus[automationState="disabled"] {{
                background-color: {colors["surface_alt"]};
                border-color: {colors["border"]};
                color: {colors["muted_text"]};
            }}
            QLabel#emptyState {{
                color: {colors["muted_text"]};
                background-color: {colors["surface"]};
                border: 1px dashed {colors["border"]};
                border-radius: 8px;
                padding: 28px;
            }}
            QMainWindow, QStackedWidget, QScrollArea {{
                background-color: {colors["background"]};
            }}
            QFrame#displayCard, QFrame#activityItem,
            QFrame#automationCard, QWidget#actionEditorCard {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 10px;
            }}
            QFrame#automationCard {{
                border-radius: 12px;
            }}
            QFrame#activityItem[eventState="success"] {{
                border-left: 3px solid {colors["configured_border"]};
            }}
            QFrame#activityItem[eventState="failed"] {{
                border-left: 3px solid {colors["unconfigured_border"]};
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
                color: {colors["primary_text"]};
                border-radius: 6px;
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
            QPushButton#primaryButton {{
                background-color: {colors["primary"]};
                color: {colors["primary_text"]};
                border-color: {colors["primary"]};
                font-weight: 700;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {colors["primary"]};
                border-color: {colors["primary"]};
            }}
            QPushButton#secondaryButton {{
                background-color: {colors["surface_alt"]};
                font-weight: 600;
            }}
            QPushButton#dangerButton:hover {{
                border-color: {colors["unconfigured_border"]};
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

    def _load_theme_file(self) -> None:
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Theme file must contain a JSON object.")

        if "themes" in data:
            self._load_themes(data["themes"])
            active_theme = data.get("active_theme", "dark")
            if not isinstance(active_theme, str) or active_theme not in self.themes:
                raise ValueError(f"Unknown active theme: {active_theme}")
            self.active_theme = active_theme
        else:
            self.themes["dark"] = self._merge_colors(
                self.themes["dark"],
                data.get("colors", {}),
            )

    def _load_themes(self, themes: object) -> None:
        if not isinstance(themes, dict) or not themes:
            raise ValueError("Theme 'themes' must be a non-empty JSON object.")

        for name, palette in themes.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Theme names must be non-empty strings.")

            defaults = self.themes.get(name, self.DEFAULT_COLORS)
            self.themes[name] = self._merge_colors(defaults, palette)

    def _merge_colors(self, defaults: dict[str, str], overrides: object) -> dict[str, str]:
        if not isinstance(overrides, dict):
            raise ValueError("Theme colors must be a JSON object.")

        unknown_colors = overrides.keys() - defaults.keys()
        if unknown_colors:
            names = ", ".join(sorted(unknown_colors))
            raise ValueError(f"Unknown theme color(s): {names}")

        colors = defaults.copy()
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

    def _save_theme_file(self) -> None:
        data = {
            "active_theme": self.active_theme,
            "themes": self.themes,
        }
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
            file.write("\n")
