#!/usr/bin/env bash
set -e
[ -f .venv/bin/activate ] && source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
