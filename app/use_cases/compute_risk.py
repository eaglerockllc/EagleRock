from datetime import datetime
from uuid import UUID
from typing import Tuple
from app.core.entities import RiskScore
from app.core.ports import EventRepositoryPort, RiskRepositoryPort

class ComputeRisk:
    """
    Heuristic risk model (baseline):
    - weather.severity in [0..1] contributes up to 0.6
    - incidents.count contributes up to 0.3
    - port_wait_min scaled contributes up to 0.1
    """
    def __init__(self, events: EventRepositoryPort, risks: RiskRepositoryPort):
        self.events = events
        self.risks = risks

    def _score(self, lane_events: list[dict]) -> Tuple[float, dict]:
        severity = 0.0
        incidents = 0
        port_wait = 0.0
        for e in lane_events:
            k = e["kind"]
            p = e["payload"] or {}
            if k == "WEATHER":
                severity = max(severity, float(p.get("severity", 0.0)))
            if k == "INCIDENT":
                incidents += 1
            if k == "PORT_STATUS":
                port_wait = max(port_wait, float(p.get("wait_min", 0.0)))
        # normalize
        s = min(1.0, 0.6*severity + 0.3*min(1.0, incidents/3.0) + 0.1*min(1.0, port_wait/120.0))
        return s, {"weather": severity, "incidents": float(incidents), "port_wait_norm": min(1.0, port_wait/120.0)}

    def execute(self, lane_id: UUID) -> RiskScore:
        events = [e.__dict__ for e in self.events.list_for_lane(lane_id, limit=100)]
        score, factors = self._score(events)
        rs = RiskScore(lane_id=lane_id, scored_at=datetime.utcnow(), score=score, top_factors=factors)
        self.risks.save(rs)
        return rs
