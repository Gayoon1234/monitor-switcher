---
title: UsbMonitorService
---

`UsbMonitorService` is a framework-independent state-diff service. It accepts
USB snapshots, compares them with the previous state, and publishes
[`DeviceEvent`](../models/Event%20Models/device-event) objects through a
framework-neutral event hook. `QtUsbMonitorAdapter` owns the Qt timer and
worker-pool execution, and passes completed snapshots to the service. USB
enumeration runs in a worker thread so a slow hardware query does not block the
Qt UI thread.

## Construction and lifecycle

```python
UsbMonitorService(device_id=None)
```

When `device_id` is provided, the service watches only that Windows device ID.
When omitted, it tracks all currently connected device IDs.

- `begin_monitoring()` resets the previous state and marks the first snapshot
  as a baseline. Devices already connected at that point do not emit events.
- `handle_state(state)` applies a completed USB snapshot and publishes only
  connection-state changes.
- `handle_poll_error(error)` logs a failed hardware read.
- `stop_monitoring()` clears any pending baseline.

The Qt adapter exposes `start(interval_ms=500)`, `set_interval(interval_ms)`,
and `stop()`. It ignores stale results after monitoring stops; an in-progress
hardware query is allowed to finish.

The application exposes the monitor enabled state and interval in Settings.
Both values are persisted under `settings` in `config.json`; monitoring is
enabled by default with a 500 ms interval.

The `device_events` event hook publishes a `DeviceEvent` with the device ID and
either `CONNECTED` or `DISCONNECTED`. In all-device mode, additions and
removals are published in sorted device-ID order for each poll.

Errors reading the monitor are logged. A failed initialization falls back to
an empty/disconnected baseline; a failed polling read emits no event and leaves
the previous state unchanged. Only one hardware query can be in flight at a
time.
