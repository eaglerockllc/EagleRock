SHELL := /bin/bash

.PHONY: up down logs seed test unit integration format lint

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

seed:
	docker compose exec -T db psql -U eaglerock -d eaglerock -f /docker-entrypoint-initdb.d/init_db.sql

test:
	docker compose run --rm api pytest -q

unit:
	docker compose run --rm api pytest -q tests/unit

integration:
	docker compose run --rm api pytest -q tests/integration

format:
	docker compose run --rm api ruff check app tests --fix

lint:
	docker compose run --rm api ruff check app tests
