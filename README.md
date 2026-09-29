# MedDocAI — project foundations

## Environment strategy

Three environments, one codebase, no branching logic in application code:

| Environment | How it's run | Secrets | Compose files |
|---|---|---|---|
| **local** | `docker compose up` on your laptop | `.env` file (gitignored, from `.env.example`) | `docker-compose.yml` + `docker-compose.override.yml` (auto-merged) |
| **staging** | CI/CD deploy to a staging cluster | injected as real env vars by a secrets manager (Vault / AWS Secrets Manager / Doppler) | `docker-compose.yml` + `docker-compose.staging.yml` (add when needed) |
| **production** | CI/CD deploy to production | same as staging, separate secret values | `docker-compose.yml` + `docker-compose.prod.yml` (add when needed) |

The rule that makes this work: `app/core/config.py` reads settings purely
from environment variables. Locally those come from `.env` (loaded by
`env_file:` in compose). In staging/production they come from real
environment variables set by the deploy pipeline — the Python code
never knows the difference, and secret values never live in git.

`docker-compose.override.yml` is loaded automatically by plain
`docker compose up`, which is exactly why local-only conveniences
(bind mounts for hot reload, exposed host ports, `--reload`) live
there instead of in `docker-compose.yml`. Staging and production
invoke compose with explicit `-f` flags and never touch the override
file, so none of that leaks into a deployed environment.

## Quickstart (local)

```bash
cp .env.example .env
make up          # builds and starts every service
make migrate      # applies Alembic migrations
make logs         # tail api / temporal-worker
```

Once it's up:
- API: http://localhost:8000/docs
- Temporal UI: http://localhost:8080
- MinIO console: http://localhost:9001
- RedisInsight: http://localhost:5540
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Project structure

```
app/
  core/         settings, security, logging
  api/v1/       FastAPI routers
  db/           SQLAlchemy models + session (source of truth, RLS lives here)
  workers/      Temporal activities (the units of work a workflow calls)
  workflows/    Temporal workflow definitions + worker process
  schemas/      Pydantic request/response models
alembic/        DB migrations
docker/         prometheus config, and future per-service configs
tests/
```

## Background work: Temporal only

There's no Celery/RabbitMQ in this stack. Temporal is the only
background-execution system — it durably retries and resumes multi-step
work (extract -> chunk -> embed -> notify) across a crash, which a plain
task queue doesn't give you for free. See `app/workflows/document_pipeline.py`
(the workflow definition) and `app/workers/activities.py` (the actual
I/O each step does). `app/workflows/worker.py` is the process that
executes them — it's the `temporal-worker` service, and it scales
horizontally by running more replicas; Temporal spreads work across
them automatically.

Redis is still here, but scoped to two things only: caching and rate
limiting (`app/core/redis.py`, wired into `fastapi-limiter` in
`app/main.py`). It has no task-queue role — see `app/api/v1/example.py`
for the rate-limiting pattern to copy onto real endpoints.

## What's stubbed vs. implemented

This scaffold gives you working local infrastructure (Postgres, Redis,
MinIO, Temporal, Prometheus, Grafana) and the DB models from the
earlier schema design, wired to a real FastAPI app with a health check
and one example rate-limited route. The activity bodies in
`app/workers/activities.py` are intentionally left as stubs — that's
the next phase: implementing the actual pipeline logic, then auth/RBAC
routes, then the human-review workflow step.

## Common commands

```bash
make up        # start the stack
make down      # stop it
make migrate   # run DB migrations
make revision m="add patients table"   # generate a new migration
make shell     # shell into the api container
make test      # run pytest
make fmt       # ruff + black
```
