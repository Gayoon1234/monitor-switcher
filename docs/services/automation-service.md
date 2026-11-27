---
title: AutomationService
---

`AutomationService` handles USB [`DeviceEvent`](../models/Event%20Models/device-event)
values, checks them against configured [`Automation`](../models/Data%20Models/automation)
objects, and executes matching actions. It depends on a `DisplayService` for
input switching and an `ActivityRepository` for history.

## Construction

```python
AutomationService(display_service, activity_repository, automations)
```

The service is a framework-independent Python class. Its `activity_events`
event hook publishes each `ActivityEvent` after it has been appended to the
repository. The Qt service-event adapter converts that hook to a Qt signal for
the UI. Activity logging is enabled by default. Its setting is restored from
`config.json`. While paused, events are neither saved to the repository nor
published, but device events continue to be handled and matching automations
still run.

## Event handling

Call `handle_device_event(event)` when the USB monitor reports a connection or
disconnection. Raw connection events are used for matching but are not written
to Activity history. The service:

1. Checks each automation, skipping disabled entries and requiring both the
   configured device ID and connected/disconnected trigger type to match.
2. Records an `automation_triggered` event and runs the matching automation's
   actions in order.

`DO_NOTHING` actions are skipped. `SWITCH_INPUT` actions call
`DisplayService.switch_input(display_id, input_id)`. A failed switch is logged
and recorded as a failed `action` event; a successful switch is recorded as a
successful `action` event. Remaining actions continue after a failure.

## Activity methods

- `get_activity_history(days=30)` delegates to `ActivityRepository.load`.
- `clear_activity_history()` clears the repository.
- `set_activity_logging_paused(paused)` pauses or resumes activity recording.

Automations are passed in at construction and held as a list; this service does
not load or save them itself.
