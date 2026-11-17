---
title: ActivityRepository
---

`ActivityRepository` persists [`ActivityEvent`](../models/Event%20Models/activity-event)
records in a SQLite database. The activity history is used to show device
events, automation triggers, and action results.

## Construction

```python
ActivityRepository(path="activity.db")
```

The path defaults to `activity.db` in the current working directory. Creating
the repository opens a SQLite connection and creates the `activity_events`
table if it does not already exist.

## Methods

- `append(event)` inserts an event's ISO-formatted timestamp, event type,
  message, and success state, then commits the write.
- `load(days=None)` returns events in insertion order. If `days` is supplied,
  it must be a positive integer and results are limited to that many days
  before the current UTC time. Timestamps are parsed back into `datetime`
  objects.
- `clear()` deletes all activity rows.
- `close()` closes the underlying SQLite connection. Close the repository when
  the application context is shut down.

The repository expects `ActivityEvent` values from the application; it does not
perform schema migrations or expose a general-purpose query API.
