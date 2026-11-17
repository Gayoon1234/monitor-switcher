---
title: UsbService
---

`UsbService` provides access to currently connected USB devices and manages
configured USB devices persisted by a `ConfigRepository`. It receives a
`UsbDeviceMonitor` for live device enumeration.

## Construction

```python
UsbService(device_monitor, repository)
```

The service is a Qt `QObject` and exposes the no-argument `devices_changed`
signal. It emits this signal after each configured-device save.

## Methods

- `get_devices()` returns the currently connected `UsbDevice` objects from the
  hardware monitor.
- `get_configured_devices()` loads and returns the saved
  `ConfiguredUsbDevice` objects.
- `add_device(device)` appends a configured device and saves the updated list.
- `remove_device(device_id)` removes all configured entries with that ID and
  saves the result.
- `update_device(device)` replaces the first saved entry with the same ID, if
  present, then saves the list.

These methods do not deduplicate additions or report whether an update matched
an existing ID.
