import time
from app.infra.config import settings
from app.infra.logging import configure_logging
from app.adapters.queue_redis import RedisEventQueue
from app.adapters.repositories import EventRepository, RiskRepository
from app.use_cases.compute_risk import ComputeRisk

log = configure_logging(settings.log_level)

def main():
    q = RedisEventQueue()
    compute = ComputeRisk(events=EventRepository(), risks=RiskRepository())
    log.info("worker_started")
    while True:
        try:
            lane_id = q.dequeue_blocking(timeout=10)
            rs = compute.execute(lane_id)
            log.info("risk_computed", lane=str(lane_id), score=rs.score)
        except TimeoutError:
            continue
        except Exception as e:
            log.exception("worker_error", err=str(e))
            time.sleep(1)

if __name__ == "__main__":
    main()
