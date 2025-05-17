from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
from uuid import UUID
from app.infra.config import settings
from app.infra.logging import configure_logging
from app.adapters.repositories import LaneRepository, EventRepository, RiskRepository, RerouteRepository
from app.adapters.queue_redis import RedisEventQueue
from app.use_cases.ingest_event import IngestEvent
from app.use_cases.compute_risk import ComputeRisk
from app.use_cases.propose_reroute import ProposeReroute

log = configure_logging(settings.log_level)
app = FastAPI(title=settings.api_title)

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

class IngestDTO(BaseModel):
    lane_id: UUID
    kind: str
    payload: dict
    source: str

@app.get("/healthz")
def healthz():
    return {"status":"ok"}

@app.get("/readiness")
def readiness():
    return {"status":"ready"}

@app.post("/api/events")
def post_event(dto: IngestDTO, _: bool = Depends(require_api_key)):
    uc = IngestEvent(events=EventRepository(), queue=RedisEventQueue())
    res = uc.execute(dto.lane_id, dto.kind, dto.payload, dto.source)
    log.info("event_ingested", lane=str(dto.lane_id), kind=dto.kind, status=res["status"])
    return res

@app.get("/api/lanes/{lane_id}/risk")
def get_risk(lane_id: UUID):
    risks = RiskRepository()
    latest = risks.latest(lane_id)
    if not latest:
        # compute on-demand
        uc = ComputeRisk(events=EventRepository(), risks=risks)
        latest = uc.execute(lane_id)
    return {"lane_id": str(lane_id), "score": latest.score, "top_factors": latest.top_factors, "model_version": latest.model_version}

@app.post("/api/lanes/{lane_id}/reroute")
def reroute(lane_id: UUID, _: bool = Depends(require_api_key)):
    uc = ProposeReroute(risks=RiskRepository(), reroutes=RerouteRepository())
    rr = uc.execute(lane_id)
    return {"lane_id": str(lane_id), "proposed_path": rr.proposed_path, "eta_delta_min": rr.eta_delta_min, "cost_delta_usd": rr.cost_delta_usd, "co2_delta_kg": rr.co2_delta_kg, "rationale": rr.rationale}
