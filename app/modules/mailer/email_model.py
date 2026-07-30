from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import List


@dataclass
class EmailRequest:
    id: str = field(default_factory=lambda: str(uuid4()))
    to: List[str] = field(default_factory=list)
    subject: str = ""
    body: str = ""
    status: str = "PENDING"
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    sent_at: datetime | None = None
