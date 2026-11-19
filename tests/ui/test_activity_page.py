from datetime import datetime

from PySide6.QtWidgets import QLabel

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


def test_activity_page_paginates_newest_events_first(qapp):
    events = [
        ActivityEvent(
            datetime(2026, 1, 1, 9, index),
            "device_event",
            f"Event {index}",
            True,
        )
        for index in range(ActivityPage.PAGE_SIZE + 1)
    ]
    page = ActivityPage(activity_history=events, days=None)

    assert page.activity_container.count() == ActivityPage.PAGE_SIZE
    assert page.page_label.text() == "Page 1 of 2"
    assert page.summary.text() == (
        f"{ActivityPage.PAGE_SIZE + 1} events  ·  "
        f"{ActivityPage.PAGE_SIZE + 1} successful  ·  0 failed"
    )
    first_item = page.activity_container.itemAt(0).widget()
    assert first_item.findChild(QLabel, "activityMessage").text() == "Event 25"

    page.next_page_button.click()
    assert page.page_label.text() == "Page 2 of 2"
    assert page.activity_container.count() == 1
    last_item = page.activity_container.itemAt(0).widget()
    assert last_item.findChild(QLabel, "activityMessage").text() == "Event 0"

    page.previous_page_button.click()
    assert page.page_label.text() == "Page 1 of 2"
    assert page.activity_container.count() == ActivityPage.PAGE_SIZE
