---
title: DisplayService
---

`DisplayService` coordinates display discovery, persisted display details, and
input switching. It receives a monitor controller, a display discovery
interface, and a `ConfigRepository`.

## Initialization

```python
DisplayService(monitor_controller, display_discovery, repository)
```

On construction, it loads displays from the repository. If none are saved, it
discovers displays and saves them. Otherwise, it discovers current display
inputs and refreshes the saved displays' `current_input` values when matching
Windows device IDs are found. Finally, it supplies the display list to the
monitor controller.

## Methods

- `get_displays()` returns the service's current display list.
- `refresh_displays()` rediscovers displays. If the result differs from the
  current list, it saves the new list, rebuilds its ID lookup, and updates the
  controller. It returns the current list.
- `switch_input(display_id, input_id)` finds the display and asks the
  controller to switch it. The in-memory `current_input` is updated only after
  the controller succeeds.

Switching an unknown display ID raises `ValueError`. Hardware/controller errors
are allowed to propagate to the caller.
