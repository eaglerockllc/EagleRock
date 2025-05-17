from uuid import UUID
from app.core.entities import RerouteProposal
from app.core.ports import RiskRepositoryPort, RerouteRepositoryPort

class ProposeReroute:
    """
    Naive reroute:
    - If risk >= 0.6 propose 'SOUTHERN_ALT' with +45 min cost and +$200, -5% CO2 (placeholder numbers)
    - Else keep 'PRIMARY'
    """
    def __init__(self, risks: RiskRepositoryPort, reroutes: RerouteRepositoryPort):
        self.risks = risks
        self.reroutes = reroutes

    def execute(self, lane_id: UUID) -> RerouteProposal:
        latest = self.risks.latest(lane_id)
        if latest and latest.score >= 0.6:
            rr = RerouteProposal(lane_id=lane_id, proposed_path="SOUTHERN_ALT", eta_delta_min=45, cost_delta_usd=200.0, co2_delta_kg=-20.0, rationale="High risk detected; detouring to avoid disruption")
        else:
            rr = RerouteProposal(lane_id=lane_id, proposed_path="PRIMARY", eta_delta_min=0, cost_delta_usd=0.0, co2_delta_kg=0.0, rationale="Risk low; proceed on primary lane")
        self.reroutes.save(rr)
        return rr
