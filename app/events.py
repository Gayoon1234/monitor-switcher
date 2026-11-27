from collections.abc import Callable
from typing import Generic, TypeVar


EventT = TypeVar("EventT")


class EventHook(Generic[EventT]):

    def __init__(self):
        self._listeners: list[Callable[[EventT], None]] = []

    def subscribe(
        self,
        listener: Callable[[EventT], None],
    ) -> Callable[[], None]:
        self._listeners.append(listener)
        subscribed = True

        def unsubscribe() -> None:
            nonlocal subscribed
            if not subscribed:
                return

            self._listeners.remove(listener)
            subscribed = False

        return unsubscribe

    def emit(self, event: EventT) -> None:
        for listener in tuple(self._listeners):
            listener(event)
