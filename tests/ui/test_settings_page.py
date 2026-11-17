from types import SimpleNamespace

from PySide6.QtWidgets import QLabel

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
    assert labels["Choose an application color theme."].wordWrap()


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

    assert repository.load_activity_days() == 7
    assert activity_page.days == 7


def test_activity_logging_button_toggles_pause_state(tmp_path, qapp):
    service = ThemeService(str(tmp_path / "theme.json"))
    page = SettingsPage(service)
    paused_states = []
    page.activity_logging_paused_changed.connect(paused_states.append)

    assert page.pause_activity_button.text() == "Pause activity logs"

    page.pause_activity_button.click()
    assert page.pause_activity_button.text() == "Resume activity logs"

    page.pause_activity_button.click()
    assert page.pause_activity_button.text() == "Pause activity logs"
    assert paused_states == [True, False]


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

    assert activity_service.activity_logging_paused is True
    assert repository.load_store_activity_logs() is False
