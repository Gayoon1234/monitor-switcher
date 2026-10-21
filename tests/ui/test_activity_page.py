from datetime import datetime

from app.models.activity_event import ActivityEvent
from app.ui.pages.activity import ActivityPage, ActivityItem


def test_activity_page_shows_event_summary_and_newest_first(qapp):
    page = ActivityPage()
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
