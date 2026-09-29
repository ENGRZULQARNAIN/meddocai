.PHONY: up down logs migrate revision shell test fmt

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api temporal-worker

migrate:
	docker compose exec api alembic upgrade head

revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

shell:
	docker compose exec api bash

test:
	docker compose exec api pytest

fmt:
	docker compose exec api ruff check --fix .
	docker compose exec api black .
