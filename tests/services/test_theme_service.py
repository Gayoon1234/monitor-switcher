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


def test_loads_available_palettes_from_theme_file(tmp_path):
    service = ThemeService("theme.json")

    assert service.get_theme_names() == [
        "dark",
        "light",
        "hacker",
        "harlequin",
    ]


def test_theme_change_is_saved_and_uses_selected_palette(tmp_path):
    path = tmp_path / "theme.json"
    service = ThemeService(str(path))

    service.set_active_theme("hacker")

    saved_theme = json.loads(path.read_text(encoding="utf-8"))
    assert service.get_active_theme() == "hacker"
    assert service.get_color("background") == "#000000"
    assert saved_theme["active_theme"] == "hacker"
    assert "hacker" in saved_theme["themes"]
    reloaded_service = ThemeService(str(path))
    assert reloaded_service.get_active_theme() == "hacker"


def test_rejects_unknown_theme_name(tmp_path):
    service = ThemeService(str(tmp_path / "missing.json"))

    with pytest.raises(ValueError, match="Unknown theme"):
        service.set_active_theme("unknown")


def test_harlequin_palette_has_readable_text_contrast(tmp_path):
    service = ThemeService("theme.json")
    palette = service.themes["harlequin"]

    def contrast_ratio(first, second):
        def luminance(color):
            channels = [
                int(color[index:index + 2], 16) / 255
                for index in (1, 3, 5)
            ]
            linear = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return (
                0.2126 * linear[0]
                + 0.7152 * linear[1]
                + 0.0722 * linear[2]
            )

        lighter, darker = sorted(
            (luminance(first), luminance(second)),
            reverse=True,
        )
        return (lighter + 0.05) / (darker + 0.05)

    for background in (
        "background",
        "surface",
        "surface_alt",
        "configured_background",
        "unconfigured_background",
    ):
        assert contrast_ratio(
            palette[background],
            palette["text"],
        ) >= 4.5

    assert contrast_ratio(
        palette["primary"],
        palette["primary_text"],
    ) >= 4.5
    assert contrast_ratio(
        palette["surface"],
        palette["muted_text"],
    ) >= 4.5
    assert palette["surface"] != palette["background"]
    assert palette["surface_alt"] != palette["surface"]
    assert palette["border"] != palette["primary"]


def test_legacy_colors_theme_file_still_loads(tmp_path):
    path = tmp_path / "theme.json"
    path.write_text(
        json.dumps({"colors": {"primary": "#123456"}}),
        encoding="utf-8",
    )

    service = ThemeService(str(path))

    assert service.get_active_theme() == "dark"
    assert service.get_color("primary") == "#123456"


def test_stylesheet_does_not_add_borders_to_every_frame(tmp_path):
    stylesheet = ThemeService(str(tmp_path / "missing.json")).get_stylesheet()

    assert "QFrame {" not in stylesheet
    assert "QScrollBar:vertical" in stylesheet
    assert "QScrollBar:horizontal" in stylesheet
    assert "QScrollBar::handle:vertical" in stylesheet
    assert "QScrollBar::handle:horizontal" in stylesheet
