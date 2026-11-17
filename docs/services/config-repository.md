---
title: ConfigRepository
---

`ConfigRepository` reads and writes the application's `config.json` file. It
serializes the configured USB devices, automations, displays, and activity
history period used by the application.

## Construction

```python
ConfigRepository(path="config.json")
```

The default path is relative to the current working directory. Loaded JSON is
cached in memory; each save updates the relevant top-level property and writes
the complete configuration back to the file, preserving other properties.

## Methods

### USB devices

- `load_usb_devices()` returns `ConfiguredUsbDevice` objects from
  `usb_devices`.
- `save_usb_devices(devices)` serializes the supplied configured devices.

### Automations

- `load_automations()` rebuilds `Automation`, `Trigger`, and `Action` objects,
  including their enum values, from `automations`.
- `save_automations(automations)` writes IDs, names, enabled state, trigger
  type and device ID, plus each action's type, display ID, and input ID.

### Displays

- `load_displays()` rebuilds `Display` and `DisplayInput` objects from
  `displays`, including each input's `InputType`.
- `save_displays(displays)` writes display identifiers and names, Windows
  device IDs, and input identifiers and types.

### Activity history

- `load_activity_days()` returns the saved history period in days, or `30` if
  no period has been saved. `None` represents all activity.
- `save_activity_days(days)` persists the selected history period.

If the file is absent or cannot be read as JSON, loading begins with an empty
configuration. The repository does not validate the full configuration schema
or provide concurrent-write coordination.
