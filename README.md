# Insurance API

A FastAPI-based vehicle lookup proxy that retrieves vehicle information via license plate.

## Features

- License plate validation (7-8 digit Israeli plates)
- Upstream API proxy with retry/backoff
- Rate limiting (30 req/min per IP)
- Structured JSON logging
- Environment-based configuration

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Or with Docker:

```bash
docker-compose up --build
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vehicle-info` | Look up vehicle by plate |
| GET | `/health` | Health check |

See [docs/api-spec.md](docs/api-spec.md) for full spec.

## Project Structure

```
src/
  api/            # HTTP routes + rate limiter
  core/           # Business logic (pure functions)
  integrations/   # Upstream API client
  models/         # Pydantic schemas
  config/         # Settings from env
  auth/           # Auth layer (placeholder)
  main.py         # App factory
tests/            # Unit, integration, e2e
docs/             # Architecture, API spec, onboarding
prompts/          # Reusable Claude prompts
scripts/          # Dev setup & run scripts
.github/          # CI pipeline
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `development` | `development` enables `/docs`; `production` disables it |
| `UPSTREAM_URL` | GCP webhook URL | Upstream vehicle info service |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |
