import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.routes import router
from src.config.settings import ALLOWED_ORIGINS, ENV
from src.core.limiter import limiter

# Structured log format: timestamp, level, logger name, message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("insurance_api")


# Runs once on startup and once on shutdown — replaces the deprecated @app.on_event pattern
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Insurance API starting up env=%s", ENV)
    yield
    logger.info("Insurance API shutting down")


# Swagger and ReDoc are disabled in production to avoid exposing the API schema
docs_url = None if ENV == "production" else "/docs"
redoc_url = None if ENV == "production" else "/redoc"

app = FastAPI(
    title="Insurance API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# slowapi requires the limiter on app.state so the rate-limit exception handler can find it
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS origins are configured via the ALLOWED_ORIGINS env var (default: "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


# Logs method, path, status, and duration for every request
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


# Catches any unhandled exception and returns a generic 500 — prevents stack traces leaking to clients
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled exception path=%s error=%s",
        request.url.path,
        type(exc).__name__,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
        },
    )


app.include_router(router)
