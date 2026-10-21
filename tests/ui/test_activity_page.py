from datetime import datetime

from app.models.activity_event import ActivityEvent
from app.ui.pages.activity import ActivityPage, ActivityItem


def test_activity_page_shows_event_summary_and_newest_first(qapp):
    page = ActivityPage(days=None)
    older = ActivityEvent(
        datetime(2026, 1, 1, 9, 0),
        "device_event",
        "Device connected",
        True,
    )
    newer = ActivityEvent(
        datetime(2026, 1, 1, 9, 1),
        "action",
        "Failed to switch display",
        False,
    )

    page.add_event(older)
    page.add_event(newer)

    assert page.summary.text() == "2 events  ·  1 successful  ·  1 failed"
    assert page.activity_container.count() == 2
    assert isinstance(page.activity_container.itemAt(0).widget(), ActivityItem)
    assert page.activity_container.itemAt(0).widget().property(
        "eventState"
    ) == "failed"


def test_activity_page_can_refresh_to_empty_and_back(qapp):
    page = ActivityPage(days=None)
    event = ActivityEvent(
        datetime.now(),
        "device_event",
        "Device connected",
        True,
    )

    page.add_event(event)
    page.set_events([])
    assert page.summary.text() == "No events yet"
    assert page.activity_container.count() == 1

    page.set_events([event])
    assert page.total_events == 1
    assert page.activity_container.count() == 1
