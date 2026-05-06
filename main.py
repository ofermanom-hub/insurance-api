# Backward-compatible shim for local dev: uvicorn main:app
# Production (Docker) runs: uvicorn src.main:app
from src.main import app  # noqa: F401
