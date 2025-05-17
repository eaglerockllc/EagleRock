from uuid import uuid4
from datetime import datetime
from app.use_cases.compute_risk import ComputeRisk
from app.core.entities import Event
from typing import List

class FakeEventsRepo:
    def __init__(self, events: List[Event]): self._events = events
    def list_for_lane(self, lane_id, limit=100): return self._events

class FakeRiskRepo:
    def __init__(self): self.saved = []
    def save(self, score): self.saved.append(score)
    def latest(self, lane_id): return None

def test_compute_risk_weather_dominates():
    lane_id = uuid4()
    evts = [
        Event(id=None, lane_id=lane_id, occurred_at=datetime.utcnow(), kind="WEATHER", payload={"severity": 0.9}, source="t", checksum="x"),
        Event(id=None, lane_id=lane_id, occurred_at=datetime.utcnow(), kind="INCIDENT", payload={}, source="t", checksum="y"),
    ]
    uc = ComputeRisk(events=FakeEventsRepo(evts), risks=FakeRiskRepo())
    rs = uc.execute(lane_id)
    assert 0.5 < rs.score <= 1.0
    assert rs.top_factors["weather"] == 0.9
