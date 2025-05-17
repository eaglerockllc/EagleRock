from __future__ import annotations
from typing import Iterable, Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.engine import Row
from app.core.entities import Lane, Event, RiskScore, RerouteProposal
from app.infra.db import SessionLocal

class LaneRepository(LaneRepositoryPort:=object):  # type: ignore
    def get(self, lane_id: UUID) -> Optional[Lane]:
        with SessionLocal() as s:
            row = s.execute(text("SELECT id, origin, destination, constraints FROM lanes WHERE id=:id"), {"id": str(lane_id)}).fetchone()
            if not row:
                return None
            return Lane(id=row[0], origin=row[1], destination=row[2], constraints=row[3] or {})

    def list(self) -> Iterable[Lane]:
        with SessionLocal() as s:
            rows = s.execute(text("SELECT id, origin, destination, constraints FROM lanes")).fetchall()
            for r in rows:
                yield Lane(id=r[0], origin=r[1], destination=r[2], constraints=r[3] or {})

class EventRepository(EventRepositoryPort:=object):  # type: ignore
    def append(self, evt: Event) -> None:
        with SessionLocal() as s:
            s.execute(
                text("""INSERT INTO events (lane_id, occurred_at, kind, payload, source, checksum)
                      VALUES (:lane_id, :occurred_at, :kind, :payload::jsonb, :source, :checksum)
                      ON CONFLICT (source, checksum) DO NOTHING"""),
                {
                    "lane_id": str(evt.lane_id),
                    "occurred_at": evt.occurred_at,
                    "kind": evt.kind,
                    "payload": json_dumps(evt.payload),
                    "source": evt.source,
                    "checksum": evt.checksum,
                },
            )
            s.commit()

    def exists_by_checksum(self, source: str, checksum: str) -> bool:
        with SessionLocal() as s:
            row = s.execute(text("SELECT 1 FROM events WHERE source=:source AND checksum=:checksum"), {"source": source, "checksum": checksum}).fetchone()
            return row is not None

    def list_for_lane(self, lane_id: UUID, limit: int = 100) -> List[Event]:
        with SessionLocal() as s:
            rows = s.execute(
                text("SELECT id, lane_id, occurred_at, kind, payload, source, checksum FROM events WHERE lane_id=:id ORDER BY occurred_at DESC LIMIT :limit"),
                {"id": str(lane_id), "limit": limit},
            ).fetchall()
            return [
                Event(
                    id=r[0], lane_id=r[1], occurred_at=r[2], kind=r[3], payload=r[4], source=r[5], checksum=r[6]
                )
                for r in rows
            ]

from orjson import dumps as json_dumps

class RiskRepository(RiskRepositoryPort:=object):  # type: ignore
    def save(self, score: RiskScore) -> None:
        with SessionLocal() as s:
            s.execute(
                text("""INSERT INTO risk_scores (lane_id, scored_at, score, top_factors, model_version)
                         VALUES (:lane_id, :scored_at, :score, :top_factors::jsonb, :model_version)"""),
                {
                    "lane_id": str(score.lane_id),
                    "scored_at": score.scored_at,
                    "score": score.score,
                    "top_factors": json_dumps(score.top_factors),
                    "model_version": score.model_version,
                },
            )
            s.commit()

    def latest(self, lane_id: UUID) -> Optional[RiskScore]:
        with SessionLocal() as s:
            r = s.execute(
                text("SELECT lane_id, scored_at, score, top_factors, model_version FROM risk_scores WHERE lane_id=:id ORDER BY scored_at DESC LIMIT 1"),
                {"id": str(lane_id)},
            ).fetchone()
            if not r:
                return None
            return RiskScore(lane_id=r[0], scored_at=r[1], score=float(r[2]), top_factors=r[3], model_version=r[4])

class RerouteRepository(RerouteRepositoryPort:=object):  # type: ignore
    def save(self, rr: RerouteProposal) -> None:
        with SessionLocal() as s:
            s.execute(
                text("""INSERT INTO reroutes (lane_id, proposed_path, eta_delta_min, cost_delta_usd, co2_delta_kg, rationale)
                         VALUES (:lane_id, :proposed_path, :eta_delta_min, :cost_delta_usd, :co2_delta_kg, :rationale)"""),
                {
                    "lane_id": str(rr.lane_id),
                    "proposed_path": rr.proposed_path,
                    "eta_delta_min": rr.eta_delta_min,
                    "cost_delta_usd": rr.cost_delta_usd,
                    "co2_delta_kg": rr.co2_delta_kg,
                    "rationale": rr.rationale,
                },
            )
            s.commit()

    def latest(self, lane_id: UUID):
        with SessionLocal() as s:
            r = s.execute(
                text("SELECT lane_id, proposed_path, eta_delta_min, cost_delta_usd, co2_delta_kg, rationale, created_at FROM reroutes WHERE lane_id=:id ORDER BY created_at DESC LIMIT 1"),
                {"id": str(lane_id)},
            ).fetchone()
            return r
