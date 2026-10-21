from app.services.theme_service import ThemeService
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
