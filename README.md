# EagleRock – AI Supply Chain Risk Mitigation & Reroute

An application that ingests supply‑chain **events**, stores them in **PostgreSQL**, computes a simple **lane risk score**, and proposes a **reroute**. It follows principles from:

- *Clean Architecture* (Layers: **core domain**, **use cases**, **adapters**, **entrypoints**)
- *Clean Code* (small functions, clear names, tests, linting)
- *Designing Data‑Intensive Applications* (immutable event log, schema evolution readiness, idempotency, backpressure via queue)

## What’s in the Application?

- **API (FastAPI)**: Ingest events, query lane risk, request reroute.
- **Worker**: Consumes queued events and computes risk in background.
- **PostgreSQL**: Durable storage; **events** (append-only), **lanes**, **risk_scores**, **reroutes**.
- **Redis**: Lightweight queue for decoupling producer/consumer.
- **Tests**: Unit & integration (pytest). CI pipeline included.
- **Docker Compose**: One command to run everything locally.

## Architecture

```
core/                 # Entities (Lane, Event), value objects, domain errors
use_cases/            # Application orchestrators (IngestEvent, ComputeRisk, ProposeReroute)
adapters/
  repositories/       # Postgres implementations of ports
  queue/              # Redis implementation of EventQueuePort
infra/                # DB session mgmt, config, logging, migrations script
entrypoints/
  api/                # FastAPI (driving adapter)
  worker/             # Background worker loop
```

### Data model

- **events**: immutable, append-only; columns: id (UUID), occurred_at, lane_id, kind, payload, source, checksum for idempotency.
- **lanes**: origin/destination + constraints.
- **risk_scores**: snapshot of risk over time with top_factors JSON.
- **reroutes**: reroute proposal (alt path string), deltas for ETA/cost.

## Quickstart

```bash
# 1) Copy .env
cp .env.sample .env

# 2) Build & run
docker compose up --build -d

# 3) Open API docs
open http://localhost:8080/docs

# 4) Seed lanes & test an event
make seed
curl -s -X POST http://localhost:8080/api/events \\
  -H 'Content-Type: application/json' \\
  -d '{"lane_id":"00000000-0000-0000-0000-000000000001","kind":"WEATHER","payload":{"severity":0.7,"region":"GREAT_LAKES"},"source":"demo"}' | jq .

# 5) Query risk
curl -s http://localhost:8080/api/lanes/00000000-0000-0000-0000-000000000001/risk | jq .

# 6) Ask for reroute
curl -s -X POST http://localhost:8080/api/lanes/00000000-0000-0000-0000-000000000001/reroute | jq .
```

## Tests

```bash
# run unit tests only
docker compose run --rm api pytest -q tests/unit

# run integration tests (requires services up)
docker compose run --rm api pytest -q tests/integration
```

## Design Choices

- **Ports & Adapters**: Domain talks to interfaces; infra is replaceable (e.g., swap Redis for Kafka later).
- **Idempotent ingest**: checksum prevents duplicates from flaky upstreams.
- **Backpressure**: queue decouples API from compute.
- **Observability**: structured logs + request IDs.
- **12‑Factor**: config via environment; stateless services.

## Infra & Security

- API key header for write endpoints.
- Basic rate limiting (token bucket in memory).
- Health checks `/healthz` and `/readiness`.

---
