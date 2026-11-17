---
title: ThemeService
---

`ThemeService` loads theme palettes, provides the active palette's colors, and
generates the Qt stylesheet used by the UI. It reads and writes `theme.json`.

## Construction and theme files

```python
ThemeService(path="theme.json")
```

The default palettes are `dark`, `light`, `hacker`, and `harlequin`. If the
file is missing, the service uses those built-in palettes and selects `dark`.
It also supports the older file shape with a single `colors` object, which
overrides colors in the default dark palette.

The current format stores an `active_theme` and a `themes` object containing
palettes. A palette may override known color names; omitted colors retain that
palette's defaults. Unknown color names, malformed palette data, invalid hex
colors, or an unknown active theme raise `ValueError`.

## Methods

- `get_color(name)` returns one color from the active palette. An unknown name
  raises `KeyError`.
- `get_colors()` returns a copy of the active palette.
- `get_theme_names()` returns available palette names.
- `get_active_theme()` returns the active theme name.
- `set_active_theme(name)` selects and persists a known theme; an unknown name
  raises `ValueError`.
- `get_stylesheet()` builds a Qt stylesheet using the active palette.

Changing the active theme writes the complete palette configuration and
selected theme to the configured path.
