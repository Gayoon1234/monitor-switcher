import json

import pytest

from app.services.theme_service import ThemeService


def test_loads_theme_colors_and_uses_defaults_for_missing_colors(tmp_path):
    path = tmp_path / "theme.json"
    path.write_text(
        json.dumps({"colors": {"primary": "#123456"}}),
        encoding="utf-8",
    )

    service = ThemeService(str(path))

    assert service.get_color("primary") == "#123456"
    assert service.get_color("background") == ThemeService.DEFAULT_COLORS[
        "background"
    ]
    assert "background-color: #123456" in service.get_stylesheet()


def test_uses_default_colors_when_theme_file_does_not_exist(tmp_path):
    service = ThemeService(str(tmp_path / "missing.json"))

    assert service.get_colors() == ThemeService.DEFAULT_COLORS
    assert service.get_color("background") == "#1e1e1e"
    assert service.get_color("text") == "#f1f1f1"


@pytest.mark.parametrize(
    "theme_data",
    [
        [],
        {"colors": []},
        {"colors": {"primary": "blue"}},
        {"colors": {"unknown": "#123456"}},
    ],
)
def test_rejects_invalid_theme_data(tmp_path, theme_data):
    path = tmp_path / "theme.json"
    path.write_text(json.dumps(theme_data), encoding="utf-8")

    with pytest.raises(ValueError):
        ThemeService(str(path))


def test_get_color_rejects_unknown_name(tmp_path):
    service = ThemeService(str(tmp_path / "missing.json"))

    with pytest.raises(KeyError, match="Unknown theme color"):
        service.get_color("unknown")


def test_stylesheet_does_not_add_borders_to_every_frame(tmp_path):
    stylesheet = ThemeService(str(tmp_path / "missing.json")).get_stylesheet()

    assert "QFrame {" not in stylesheet
    assert "QScrollBar:vertical" in stylesheet
    assert "QScrollBar:horizontal" in stylesheet
    assert "QScrollBar::handle:vertical" in stylesheet
    assert "QScrollBar::handle:horizontal" in stylesheet
