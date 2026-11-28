from types import SimpleNamespace

from PySide6.QtWidgets import QFrame, QLabel

from app.models.config import ConfigKey
from app.services.config_repository import ConfigRepository
from app.services.theme_service import ThemeService
from app.ui.main_window import MainWindow
from app.ui.pages.settings import SettingsPage


def test_theme_selection_emits_selected_theme(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    selected_themes = []
    page.theme_changed.connect(selected_themes.append)

    page.theme_selector.setCurrentIndex(
        page.theme_selector.findData("harlequin")
    )

    assert selected_themes == ["harlequin"]


def test_color_theme_section_uses_activity_history_heading_style(
    tmp_path,
    qapp,
):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    labels = {
        label.text(): label
        for label in page.findChildren(QLabel)
    }

    assert labels["Color theme"].objectName() == "sectionTitle"
    assert "Choose an application color theme." not in labels


def test_settings_sections_use_theme_cards(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)

    sections = page.findChildren(QFrame, "settingsSectionCard")

    assert len(sections) == 3
    assert "QFrame#settingsSectionCard" in service.get_stylesheet()


def test_activity_period_selection_emits_retention_days(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    selected_periods = []
    page.activity_days_changed.connect(selected_periods.append)

    page.activity_period_selector.setCurrentIndex(
        page.activity_period_selector.findData(None)
    )
    page.activity_period_selector.setCurrentIndex(
        page.activity_period_selector.findData(7)
    )

    assert selected_periods == [None, 7]


def test_selected_activity_period_is_saved(tmp_path):
    repository = ConfigRepository(path=tmp_path / "config.json")
    activity_page = SimpleNamespace(days=30, set_events=lambda events: None)
    activity_service = SimpleNamespace(get_activity_history=lambda days: [])
    window = SimpleNamespace(
        repository=repository,
        activity_page=activity_page,
        automation_service=activity_service,
    )

    MainWindow._set_activity_period(window, 7)

    assert repository.get_config(ConfigKey.ACTIVITY_DAYS) == 7
    assert activity_page.days == 7


def test_activity_logging_button_toggles_pause_state(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    paused_states = []
    page.activity_logging_paused_changed.connect(paused_states.append)

    assert page.activity_logging_button.text() == (
        "Click to pause Activity Logs"
    )

    page.activity_logging_button.click()
    assert page.activity_logging_button.text() == (
        "Click to start recording Activity Logs"
    )

    page.activity_logging_button.click()
    assert page.activity_logging_button.text() == (
        "Click to pause Activity Logs"
    )
    assert paused_states == [True, False]


def test_delete_activity_button_uses_danger_style(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    stylesheet = service.get_stylesheet()

    assert page.clear_activity_button.objectName() == "dangerButton"
    assert "background-color: #b42318" in stylesheet


def test_activity_controls_expand_across_two_rows(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    labels = [
        label.text()
        for label in page.findChildren(QLabel)
    ]

    assert "Show activity from:" in labels
    assert page.activity_filter_row.stretch(1) == 1
    assert page.activity_actions_row.stretch(1) == 1
    assert page.activity_actions_row.stretch(0) == 1
    assert "Choose how much history to show." not in labels


def test_settings_page_has_consistent_margins_and_spacing(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)

    assert page.layout().spacing() == 16
    assert page.layout().contentsMargins().left() == 24
    assert page.layout().contentsMargins().top() == 20


def test_activity_logging_pause_is_persisted(tmp_path):
    repository = ConfigRepository(path=tmp_path / "config.json")
    activity_service = SimpleNamespace(
        activity_logging_paused=False,
        set_activity_logging_paused=lambda paused: setattr(
            activity_service,
            "activity_logging_paused",
            paused,
        ),
    )
    window = SimpleNamespace(
        repository=repository,
        automation_service=activity_service,
    )

    MainWindow._set_activity_logging_paused(window, True)

    assert repository.get_config(ConfigKey.STORE_ACTIVITY_LOGS) is False


def test_usb_monitor_settings_emit_changes(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    enabled_states = []
    intervals = []
    page.usb_monitor_enabled_changed.connect(enabled_states.append)
    page.usb_monitor_interval_changed.connect(intervals.append)

    assert page.usb_monitor_button.text() == (
        "Click to stop USB device monitoring"
    )

    page.usb_monitor_button.click()
    assert page.usb_monitor_button.text() == (
        "Click to start USB device monitoring"
    )
    page.usb_monitor_button.click()
    assert page.usb_monitor_button.text() == (
        "Click to stop USB device monitoring"
    )
    page.usb_monitor_interval_spinbox.setValue(1000)

    assert enabled_states == [False, True]
    assert intervals == [1000]


def test_usb_monitor_settings_update_service_and_persist(tmp_path):
    repository = ConfigRepository(path=tmp_path / "config.json")
    calls = []

    class FakeUsbMonitorAdapter:
        def start(self, interval_ms):
            calls.append(("start", interval_ms))

        def stop(self):
            calls.append(("stop",))

        def set_interval(self, interval_ms):
            calls.append(("interval", interval_ms))

    window = SimpleNamespace(
        repository=repository,
        usb_monitor_adapter=FakeUsbMonitorAdapter(),
    )

    MainWindow._set_usb_monitor_enabled(window, False)
    MainWindow._set_usb_monitor_interval(window, 250)
    MainWindow._set_usb_monitor_enabled(window, True)

    assert calls == [("stop",), ("interval", 250), ("start", 250)]
    assert repository.get_config(ConfigKey.USB_MONITOR_ENABLED) is True
    assert repository.get_config(ConfigKey.USB_MONITOR_INTERVAL_MS) == 250
