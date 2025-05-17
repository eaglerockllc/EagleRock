from dataclasses import asdict
from datetime import datetime
from uuid import UUID
import hashlib
from app.core.entities import Event
from app.core.ports import EventRepositoryPort, EventQueuePort

class IngestEvent:
    def __init__(self, events: EventRepositoryPort, queue: EventQueuePort):
        self.events = events
        self.queue = queue

    def _checksum(self, lane_id: UUID, kind: str, payload: dict, source: str) -> str:
        m = hashlib.sha256()
        m.update(str(lane_id).encode())
        m.update(kind.encode())
        m.update(str(sorted(payload.items())).encode())
        m.update(source.encode())
        return m.hexdigest()

    def execute(self, lane_id: UUID, kind: str, payload: dict, source: str) -> dict:
        checksum = self._checksum(lane_id, kind, payload, source)
        if self.events.exists_by_checksum(source, checksum):
            return {"status":"duplicate","checksum":checksum}
        evt = Event(id=None, lane_id=lane_id, occurred_at=datetime.utcnow(), kind=kind, payload=payload, source=source, checksum=checksum)
        self.events.append(evt)
        # push to queue for risk compute
        self.queue.enqueue(lane_id)
        return {"status":"accepted","checksum":checksum}
