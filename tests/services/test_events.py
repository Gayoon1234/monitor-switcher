from app.events import EventHook


def test_event_hook_notifies_subscribers_and_supports_unsubscribe():
    event_hook: EventHook[str] = EventHook()
    received = []
    unsubscribe = event_hook.subscribe(received.append)

    event_hook.emit("first")
    unsubscribe()
    unsubscribe()
    event_hook.emit("second")

    assert received == ["first"]
