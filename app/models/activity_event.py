from dataclasses import dataclass
from datetime import datetime

# To record application logs.
# We only log automation triggers at this point
@dataclass
class ActivityEvent:
    timestamp: datetime
    event_type: str
    message: str
    success: bool