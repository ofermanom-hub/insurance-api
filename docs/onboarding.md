# Onboarding Guide

## Prerequisites

- Python 3.11+
- Docker + Docker Compose (optional)

## Local Setup

```bash
git clone https://github.com/ofermanom-hub/insurance-api
cd insurance-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

API: http://localhost:8080
Swagger: http://localhost:8080/docs

## Docker

```bash
docker-compose up --build
```

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project Layout

| Path | What is there |
|------|--------------|
| `src/api/` | Routes, rate limiter |
| `src/core/` | Business logic |
| `src/integrations/` | Upstream API client |
| `src/models/` | Pydantic schemas |
| `src/config/` | Env-based settings |
| `prompts/` | Reusable Claude prompts |

## Using the Claude Prompts

| File | Use it for |
|------|-----------|
| `code_review.md` | PR reviews |
| `test_generation.md` | Writing tests |
| `security_review.md` | Auth/security audit |
| `refactor.md` | Improving structure |
| `full_pipeline.md` | Generate all delivery outputs |
