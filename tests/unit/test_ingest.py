from uuid import uuid4
from app.use_cases.ingest_event import IngestEvent

class FakeEvents:
    def __init__(self): self.items = []
    def append(self, e): self.items.append(e)
    def exists_by_checksum(self, source, checksum): return False

class FakeQueue:
    def __init__(self): self.items = []
    def enqueue(self, lane_id): self.items.append(lane_id)

def test_ingest_enqueue_once():
    uc = IngestEvent(events=FakeEvents(), queue=FakeQueue())
    lane_id = uuid4()
    res = uc.execute(lane_id, "WEATHER", {"severity":0.8}, "demo")
    assert res["status"] == "accepted"
