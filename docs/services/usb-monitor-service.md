---
title: UsbMonitorService
---

`UsbMonitorService` polls a `UsbDeviceMonitor` and emits
[`DeviceEvent`](../models/Event%20Models/device-event) when a device's
connection state changes. It is a Qt `QObject` that uses a `QTimer`.

## Construction and lifecycle

```python
UsbMonitorService(device_monitor, device_id=None)
```

When `device_id` is provided, the service watches only that Windows device ID.
When omitted, it tracks all currently connected device IDs.

- `start(interval_ms=500)` reads the initial state, then starts polling at the
  given interval. The initial read establishes a baseline; it does not emit
  events for devices already connected.
- `stop()` stops the timer.

The `device_event` signal emits a `DeviceEvent` with the device ID and either
`CONNECTED` or `DISCONNECTED`. In all-device mode, additions and removals are
emitted in sorted device-ID order for each poll.

Errors reading the monitor are logged. A failed initialization falls back to
an empty/disconnected baseline; a failed polling read emits no event and leaves
the previous state unchanged.
