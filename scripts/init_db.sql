CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS lanes (
  id UUID PRIMARY KEY,
  origin TEXT NOT NULL,
  destination TEXT NOT NULL,
  constraints JSONB DEFAULT '{{}}'::jsonb
);

CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lane_id UUID REFERENCES lanes(id) ON DELETE CASCADE,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  kind TEXT NOT NULL,
  payload JSONB NOT NULL,
  source TEXT NOT NULL,
  checksum TEXT NOT NULL,
  UNIQUE(source, checksum)
);

CREATE TABLE IF NOT EXISTS risk_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lane_id UUID REFERENCES lanes(id) ON DELETE CASCADE,
  scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  score NUMERIC NOT NULL,
  top_factors JSONB NOT NULL,
  model_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reroutes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lane_id UUID REFERENCES lanes(id) ON DELETE CASCADE,
  proposed_path TEXT NOT NULL,
  eta_delta_min INT NOT NULL,
  cost_delta_usd NUMERIC NOT NULL,
  co2_delta_kg NUMERIC NOT NULL,
  rationale TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed a couple lanes (fixed UUIDs for docs/tests)
INSERT INTO lanes (id, origin, destination) VALUES
  ('00000000-0000-0000-0000-000000000001','Chicago, IL','New York, NY')
ON CONFLICT (id) DO NOTHING;

INSERT INTO lanes (id, origin, destination) VALUES
  ('00000000-0000-0000-0000-000000000002','Dallas, TX','Los Angeles, CA')
ON CONFLICT (id) DO NOTHING;
