from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class Lane:
    id: UUID
    origin: str
    destination: str
    constraints: Dict[str, Any] | None = None

@dataclass(frozen=True)
class Event:
    id: UUID | None
    lane_id: UUID
    occurred_at: datetime
    kind: str
    payload: Dict[str, Any]
    source: str
    checksum: str

@dataclass(frozen=True)
class RiskScore:
    lane_id: UUID
    scored_at: datetime
    score: float
    top_factors: Dict[str, float]
    model_version: str = "heuristic-v1"

@dataclass(frozen=True)
class RerouteProposal:
    lane_id: UUID
    proposed_path: str
    eta_delta_min: int
    cost_delta_usd: float
    co2_delta_kg: float
    rationale: str
