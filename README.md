# Insurance API

A FastAPI-based vehicle lookup proxy — validates Israeli license plates and retrieves vehicle data from an upstream service.

Built with an enterprise-grade layered structure, full CI pipeline, and an AI-powered delivery stack.

---

## Features

- License plate validation (7–8 digit Israeli plates)
- Upstream API proxy with retry + exponential backoff (3 attempts)
- Rate limiting — 30 req/min per IP (slowapi)
- Structured JSON logging with plate masking (PII-safe)
- Environment-based Swagger UI (disabled in production)

---

## Quick Start

```bash
# 1. Clone & configure
git clone https://github.com/ofermanom-hub/insurance-api
cd insurance-api
cp .env.example .env

# 2. Install & run
pip install -r requirements.txt
uvicorn src.main:app --reload
```

API:     http://localhost:8080  
Swagger: http://localhost:8080/docs

**Or with Docker:**

```bash
docker-compose up --build
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vehicle-info` | Look up vehicle by license plate |
| GET  | `/health`        | Health check |

Full spec → [docs/api-spec.md](docs/api-spec.md)

---

## Project Structure

```
insurance-api/
│
├── src/
│   ├── api/               # HTTP routes, rate limiter
│   ├── core/              # Business logic (pure, testable)
│   ├── integrations/      # Upstream API client + retry
│   ├── models/            # Pydantic schemas
│   ├── config/            # Env-based settings
│   ├── auth/              # Auth layer (placeholder: JWT/SAML)
│   └── main.py            # App factory
│
├── tests/
│   ├── unit/              # Pure logic tests (no HTTP)
│   ├── integration/       # Placeholder
│   └── e2e/               # Placeholder
│
├── docs/
│   ├── architecture.md    # Layer diagram + design decisions
│   ├── api-spec.md        # Full endpoint reference
│   ├── onboarding.md      # New developer guide
│   ├── project-manifest.json  # Single source of truth (risks, metrics, onboarding)
│   ├── delivery-pipeline.md   # How manifest feeds external tools
│   └── decisions/         # ADRs
│
├── prompts/               # Reusable Claude prompts
│   ├── code_review.md
│   ├── test_generation.md
│   ├── security_review.md
│   ├── refactor.md
│   ├── gamma_risks.md         # Generate Gamma risk slides
│   ├── dashboard_config.md    # Generate Grafana dashboard JSON
│   ├── monday_board.md        # Generate Monday.com board
│   ├── notion_workspace.md    # Generate Notion wiki
│   └── full_pipeline.md       # All delivery outputs in one run
│
├── scripts/
│   ├── setup.sh           # First-time environment setup
│   ├── run_local.sh       # Local dev runner
│   └── seed_data.sh       # Placeholder
│
├── tools/
│   └── ai_helpers/        # AI pipeline documentation
│
├── .github/workflows/ci.yml   # CI: pytest + flake8
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Architecture

```
Client
  └─ POST /vehicle-info
       └─ src/api/routes.py        (input validation, rate limit)
            └─ src/core/vehicle_lookup.py     (business logic)
                 └─ src/integrations/vehicle_service.py  (upstream HTTP + retry)
                 ← (vehicle dict, error_code)
            ← (vehicle dict, error_code, http_status)
       ← JSON response
```

Full details → [docs/architecture.md](docs/architecture.md)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `development` | Set to `production` to disable `/docs` and `/redoc` |
| `UPSTREAM_URL` | GCP webhook URL | Upstream vehicle info service |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## CI

Every push and pull request to `main` runs:
- `pytest tests/`
- `flake8 src/`

See [.github/workflows/ci.yml](.github/workflows/ci.yml)

---

## AI Delivery Pipeline

`docs/project-manifest.json` is the single source of truth for this project.
The `prompts/` directory contains Claude prompts that convert it into outputs for external tools:

| Prompt | Output | Tool |
|--------|--------|------|
| `gamma_risks.md` | Risk presentation | Gamma AI |
| `dashboard_config.md` | Metrics dashboard JSON | Grafana / Datadog |
| `monday_board.md` | Project board | Monday.com |
| `notion_workspace.md` | Knowledge base | Notion |
| `full_pipeline.md` | All of the above | — |

Paste the manifest + prompt into Claude → paste output into the target tool.

Details → [docs/delivery-pipeline.md](docs/delivery-pipeline.md)
