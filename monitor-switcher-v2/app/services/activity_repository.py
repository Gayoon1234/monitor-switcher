import json
from datetime import datetime
from pathlib import Path

from app.models.activity_event import ActivityEvent


class ActivityRepository:

    def __init__(self, path: str = "logs.json"):
        self.path = Path(path)

    def load(self) -> list[ActivityEvent]:
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [
            ActivityEvent(
                timestamp=datetime.fromisoformat(event["timestamp"]),
                event_type=event["event_type"],
                message=event["message"],
                success=event["success"],
            )
            for event in data.get("events", [])
        ]

    def save(self, events: list[ActivityEvent]) -> None:
        data = {
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "message": event.message,
                    "success": event.success,
                }
                for event in events
            ]
        }

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)