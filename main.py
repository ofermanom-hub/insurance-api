import asyncio
import logging
import os
import re
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("insurance_api")

UPSTREAM = os.environ.get(
    "UPSTREAM_URL",
    "https://insurance-webhook-945894769129.us-central1.run.app/vehicle-info",
)
TIMEOUT_SECONDS = 5
MAX_RETRIES = 3
ENV = os.environ.get("ENV", "development")

limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])


def _mask_plate(plate: str) -> str:
    return "****" + plate[-2:] if len(plate) >= 2 else "****"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Insurance API starting up env=%s", ENV)
    yield
    logger.info("Insurance API shutting down")


docs_url = None if ENV == "production" else "/docs"
redoc_url = None if ENV == "production" else "/redoc"

app = FastAPI(
    title="Insurance API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request completed method=%s path=%s status=%d duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


class PlateRequest(BaseModel):
    license_plate: str = Field(min_length=7, max_length=8)

    @field_validator("license_plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        cleaned = v.strip()
        if not re.fullmatch(r"\d{7,8}", cleaned):
            raise ValueError("License plate must be 7–8 digits")
        return cleaned


class VehicleData(BaseModel):
    license_plate: str
    manufacturer: str
    model: str
    year: str
    color: str


def _parse_upstream_response(raw: dict) -> dict | None:
    """Return a sanitized vehicle dict, or None if the shape is unexpected."""
    try:
        data = raw.get("data", {})
        return VehicleData(
            license_plate=str(data["license_plate"]),
            manufacturer=str(data["manufacturer"]),
            model=str(data["model"]),
            year=str(data["year"]),
            color=str(data["color"]),
        ).model_dump()
    except (KeyError, ValueError):
        return None


@app.post("/vehicle-info")
@limiter.limit("30/minute")
async def vehicle_info(req: PlateRequest, request: Request):
    masked = _mask_plate(req.license_plate)
    logger.info("vehicle lookup requested plate=%s", masked)

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                r = await client.post(UPSTREAM, json={"license_plate": req.license_plate})

            if r.status_code == 200:
                raw = r.json()
                vehicle = _parse_upstream_response(raw)
                if vehicle is None:
                    logger.error("upstream response malformed plate=%s body=%s", masked, raw)
                    return JSONResponse(
                        status_code=502,
                        content={
                            "success": False,
                            "error": {"code": "UPSTREAM_MALFORMED", "message": "Unexpected response from vehicle service"},
                        },
                    )
                logger.info("vehicle found plate=%s manufacturer=%s", masked, vehicle["manufacturer"])
                return {"success": True, "data": vehicle}

            if r.status_code == 404:
                logger.info("vehicle not found plate=%s", masked)
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": {"code": "NOT_FOUND", "message": "Vehicle not found"},
                    },
                )

            logger.warning(
                "upstream unexpected status plate=%s status=%d attempt=%d",
                masked,
                r.status_code,
                attempt + 1,
            )

        except httpx.TimeoutException:
            logger.warning("upstream timeout plate=%s attempt=%d/%d", masked, attempt + 1, MAX_RETRIES)

        except httpx.RequestError as exc:
            logger.warning(
                "upstream connection error plate=%s attempt=%d/%d error=%s",
                masked,
                attempt + 1,
                MAX_RETRIES,
                type(exc).__name__,
            )

        if attempt < MAX_RETRIES - 1:
            backoff = 0.5 * (attempt + 1)
            logger.info("retrying after %.1fs", backoff)
            await asyncio.sleep(backoff)

    logger.error("all retries exhausted plate=%s", masked)
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "error": {
                "code": "UPSTREAM_UNAVAILABLE",
                "message": "Service temporarily unavailable. Please try again shortly.",
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled exception path=%s error=%s", request.url.path, type(exc).__name__, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
