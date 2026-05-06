import os

UPSTREAM_URL = os.environ.get(
    "UPSTREAM_URL",
    "https://insurance-webhook-945894769129.us-central1.run.app/vehicle-info",
)
TIMEOUT_SECONDS = 5
MAX_RETRIES = 3
BACKOFF_BASE = 0.5
ENV = os.environ.get("ENV", "development")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
