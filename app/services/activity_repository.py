import sqlite3
from datetime import datetime
from pathlib import Path

from app.models.activity_event import ActivityEvent


class ActivityRepository:

    def __init__(self, path: str = "activity.db"):
        self.path = Path(path)
        self._connection = sqlite3.connect(self.path)
        self._create_table()

    def _create_table(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                success INTEGER NOT NULL
            )
            """
        )
        self._connection.commit()

    def append(self, event: ActivityEvent) -> None:
        self._connection.execute(
            """
            INSERT INTO activity_events (
                timestamp,
                event_type,
                message,
                success
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                event.timestamp.isoformat(),
                event.event_type,
                event.message,
                int(event.success),
            ),
        )
        self._connection.commit()

    def load(self) -> list[ActivityEvent]:
        cursor = self._connection.execute(
            """
            SELECT timestamp, event_type, message, success
            FROM activity_events
            ORDER BY id ASC
            """
        )

        return [
            ActivityEvent(
                timestamp=datetime.fromisoformat(timestamp),
                event_type=event_type,
                message=message,
                success=bool(success),
            )
            for timestamp, event_type, message, success in cursor.fetchall()
        ]

    def close(self) -> None:
        self._connection.close()