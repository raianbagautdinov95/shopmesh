from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class EventEnvelope:
    name: str
    payload: dict
    event_id: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.event_id:
            self.event_id = str(uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def as_dict(self) -> dict:
        return asdict(self)

class EventPublisher:
    def publish(self, name: str, payload: dict) -> EventEnvelope:
        envelope = EventEnvelope(name=name, payload=payload)
        return envelope
