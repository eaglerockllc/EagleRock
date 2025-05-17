import os
import pytest
import httpx
from time import sleep

API = "http://eaglerock-api:8080"
API_KEY = os.getenv("API_KEY","dev-secret-key")

@pytest.mark.integration
def test_health_and_event_flow():
    # health
    r = httpx.get(f"{API}/healthz", timeout=10.0)
    assert r.status_code == 200

    # event
    payload = {
        "lane_id":"00000000-0000-0000-0000-000000000001",
        "kind":"WEATHER",
        "payload":{"severity":0.8},
        "source":"itest"
    }
    r = httpx.post(f"{API}/api/events", headers={"x-api-key": API_KEY}, json=payload, timeout=10.0)
    assert r.status_code == 200

    # give worker a moment
    sleep(1.5)

    # risk
    r = httpx.get(f"{API}/api/lanes/00000000-0000-0000-0000-000000000001/risk", timeout=10.0)
    assert r.status_code == 200
    assert "score" in r.json()
