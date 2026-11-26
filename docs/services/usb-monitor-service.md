---
title: UsbMonitorService
---

`UsbMonitorService` polls a `UsbDeviceMonitor` and emits
[`DeviceEvent`](../models/Event%20Models/device-event) when a device's
connection state changes. `UsbDevicePoller` owns the Qt timer and worker-pool
execution; `UsbMonitorService` applies the resulting states and emits device
events. USB enumeration runs in a worker thread so a slow hardware query does
not block the Qt UI thread.

## Construction and lifecycle

```python
UsbMonitorService(device_monitor, device_id=None)
```

When `device_id` is provided, the service watches only that Windows device ID.
When omitted, it tracks all currently connected device IDs.

- `start(interval_ms=500)` starts polling at the given interval. The initial
  read runs asynchronously and establishes a baseline; it does not emit events
  for devices already connected.
- `set_interval(interval_ms)` changes the polling interval immediately.
- `stop()` stops scheduling polls. An in-progress hardware query is allowed to
  finish, but its result is ignored.

The application exposes the monitor enabled state and interval in Settings.
Both values are persisted under `settings` in `config.json`; monitoring is
enabled by default with a 500 ms interval.

The `device_event` signal emits a `DeviceEvent` with the device ID and either
`CONNECTED` or `DISCONNECTED`. In all-device mode, additions and removals are
emitted in sorted device-ID order for each poll.

Errors reading the monitor are logged. A failed initialization falls back to
an empty/disconnected baseline; a failed polling read emits no event and leaves
the previous state unchanged. Only one hardware query can be in flight at a
time.
