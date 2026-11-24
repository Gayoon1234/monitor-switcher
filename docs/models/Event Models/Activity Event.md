---
id: activity-event
title: Activity Event
sidebar_position: 1
---

## Activity events

The `ActivityEvent` model stores automation-trigger and action outcomes.
Raw USB connection events are used to evaluate automation triggers but are not
stored as new Activity events.

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
- `event_type`: `automation_triggered` or `action` for newly recorded events.
  Older databases may still contain `device_event` records; the repository
  excludes those legacy records from loaded Activity history.
- `message`: A free-text field used to describe the event.
- `success`: A Boolean value that is set to `false` when an event is emitted from a catch block after the internal code interacts with hardware.
