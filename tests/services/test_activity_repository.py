from datetime import datetime
from datetime import timedelta

import pytest
from app.models.activity_event import ActivityEvent
from app.services.activity_repository import ActivityRepository


def create_event(
    timestamp: datetime = datetime(2026, 10, 3, 12, 0, 0),
    event_type: str = "test",
    message: str = "Test event",
    success: bool = True,
) -> ActivityEvent:
    return ActivityEvent(
        timestamp=timestamp,
        event_type=event_type,
        message=message,
        success=success,
    )

def test_new_repository_has_no_events(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")

    try:
        assert repository.load() == []
    finally:
        repository.close()


def test_append_and_load_round_trip(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")

    event = create_event(
        timestamp=datetime(2026, 10, 3, 12, 30, 45),
        event_type="automation_triggered",
        message="Automation triggered: Test",
        success=True,
    )

    try:
        repository.append(event)

        assert repository.load() == [event]
    finally:
        repository.close()


def test_append_preserves_order(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")

    first = create_event(
        timestamp=datetime(2026, 10, 3, 12, 0, 0),
        message="First",
    )
    second = create_event(
        timestamp=datetime(2026, 10, 3, 11, 0, 0),
        message="Second",
    )
    third = create_event(
        timestamp=datetime(2026, 10, 3, 13, 0, 0),
        message="Third",
    )

    try:
        repository.append(first)
        repository.append(second)
        repository.append(third)

        assert repository.load() == [first, second, third]
    finally:
        repository.close()


def test_failed_event_round_trip(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")

    event = create_event(
        event_type="action",
        message="Failed to switch display",
        success=False,
    )

    try:
        repository.append(event)

        loaded = repository.load()

        assert loaded == [event]
        assert loaded[0].success is False
    finally:
        repository.close()


def test_events_persist_across_repository_instances(tmp_path):
    database_path = tmp_path / "activity.db"

    event = create_event(
        event_type="device_event",
        message="Device connected",
    )

    first_repository = ActivityRepository(database_path)
    first_repository.append(event)
    first_repository.close()

    second_repository = ActivityRepository(database_path)

    try:
        assert second_repository.load() == [event]
    finally:
        second_repository.close()


def test_load_filters_old_events_without_deleting_them(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")
    old_event = create_event(
        timestamp=datetime.now() - timedelta(days=31),
        message="Old event",
    )
    recent_event = create_event(
        timestamp=datetime.now() - timedelta(days=2),
        message="Recent event",
    )

    try:
        repository.append(old_event)
        repository.append(recent_event)

        assert repository.load(30) == [recent_event]
        assert repository.load() == [old_event, recent_event]
    finally:
        repository.close()


def test_clear_deletes_all_activity_events(tmp_path):
    repository = ActivityRepository(tmp_path / "activity.db")
    repository.append(create_event())

    try:
        repository.clear()

        assert repository.load() == []
    finally:
        repository.close()


@pytest.mark.parametrize("days", [0, -1, 1.5, "30"])
def test_load_rejects_invalid_day_count(tmp_path, days):
    repository = ActivityRepository(tmp_path / "activity.db")

    try:
        with pytest.raises(ValueError):
            repository.load(days)
    finally:
        repository.close()
