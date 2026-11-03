---
id: activity-event
title: Activity Event
sidebar_position: 1
---

## Activity events

The `ActivityEvent` model is used to store when certain events are triggered. These can be automations being triggered, displays changing, or devices connecting/disconnecting.

For example, if an automation is triggered, that would create a "Automation triggered" event, then if that automation defines multiple actions, each action will create an additional event.

These events are stored in the activity database, which is a SQLite database. It generates the most logs.

In the UI there is a dedicated `Activity` tab that lets the user view recent events. The `Settings` tab allows the user to change the time period for when logs are shown, as well as the option to delete all logs.

## Model definition

```python
@dataclass
class ActivityEvent:
    timestamp: datetime
    event_type: str
    message: str
    success: bool
```

- `timestamp`: Automatically added by the automation service methods that create events.
- `event_type`: This can be `device_event`, `automation_triggered`, or `action`, although there is no hard validation.
- `message`: A free-text field used to describe the event.
- `success`: A Boolean value that is set to `false` when an event is emitted from a catch block after the internal code interacts with hardware.
