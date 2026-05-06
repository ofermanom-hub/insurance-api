import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.core.limiter import limiter
from src.core.vehicle_lookup import lookup_vehicle
from src.models.vehicle import PlateRequest

logger = logging.getLogger("insurance_api.api.routes")

router = APIRouter()

_ERROR_MESSAGES: dict[str, str] = {
    "NOT_FOUND": "Vehicle not found",
    "UPSTREAM_MALFORMED": "Unexpected response from vehicle service",
    "UPSTREAM_UNAVAILABLE": "Service temporarily unavailable. Please try again shortly.",
}


@router.post("/vehicle-info")
@limiter.limit("30/minute")
async def vehicle_info(req: PlateRequest, request: Request):
    vehicle, error_code, status = await lookup_vehicle(req.license_plate)

    if error_code is None:
        return {"success": True, "data": vehicle}

    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": _ERROR_MESSAGES.get(error_code, "Unknown error"),
            },
        },
    )


@router.get("/health")
def health():
    return {"status": "ok"}
