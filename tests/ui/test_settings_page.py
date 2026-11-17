from types import SimpleNamespace

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
