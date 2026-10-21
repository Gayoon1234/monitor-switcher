import sqlite3
from datetime import datetime, timedelta, timezone
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

    def load(self, days: int | None = None) -> list[ActivityEvent]:
        if days is not None and (not isinstance(days, int) or days <= 0):
            raise ValueError("Activity history days must be a positive integer.")

        query = """
            SELECT timestamp, event_type, message, success
            FROM activity_events
        """
        parameters = ()
        if days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query += " WHERE julianday(timestamp) >= julianday(?)"
            parameters = (cutoff.isoformat(),)
        query += " ORDER BY id ASC"

        cursor = self._connection.execute(
            query,
            parameters,
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

    def clear(self) -> None:
        self._connection.execute("DELETE FROM activity_events")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()