from dataclasses import dataclass
from datetime import datetime


@dataclass
class ActivityEvent:
    timestamp: datetime
    event_type: str
    message: str
    success: bool