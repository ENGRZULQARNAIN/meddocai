# Multi-stage build: the same image definition is used for local
# development and production, just at different build targets, so
# you're never testing against a fundamentally different image than
# the one that actually ships.
#
# Dependencies are managed with uv (https://docs.astral.sh/uv/) from
# pyproject.toml + uv.lock. To add/upgrade a package, run `uv add <pkg>`
# (or `uv lock --upgrade`) on your machine and commit both files; the
# build installs exactly what's in uv.lock (--locked fails if it's stale).

FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# --- local development target ---
FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- production target ---
FROM base AS prod
COPY . .
RUN adduser --disabled-password --no-create-home appuser
USER appuser
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
