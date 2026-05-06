import logging

from src.core.utils import mask_plate
from src.integrations.vehicle_service import fetch_vehicle_info

logger = logging.getLogger("insurance_api.core.vehicle_lookup")

_STATUS_MAP: dict[str, int] = {
    "NOT_FOUND": 404,
    "UPSTREAM_MALFORMED": 502,
    "UPSTREAM_UNAVAILABLE": 503,
}


async def lookup_vehicle(license_plate: str) -> tuple[dict | None, str | None, int]:
    masked = mask_plate(license_plate)
    logger.info("vehicle lookup requested plate=%s", masked)
    vehicle, error_code = await fetch_vehicle_info(license_plate)
    status = _STATUS_MAP.get(error_code, 500) if error_code else 200
    return vehicle, error_code, status
