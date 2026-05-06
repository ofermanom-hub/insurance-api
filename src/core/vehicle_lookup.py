import logging

from src.integrations.vehicle_service import fetch_vehicle_info

logger = logging.getLogger("insurance_api.core.vehicle_lookup")

_STATUS_MAP: dict[str, int] = {
    "NOT_FOUND": 404,
    "UPSTREAM_MALFORMED": 502,
    "UPSTREAM_UNAVAILABLE": 503,
}


def _mask_plate(plate: str) -> str:
    return "****" + plate[-2:] if len(plate) >= 2 else "****"


async def lookup_vehicle(license_plate: str) -> tuple[dict | None, str | None, int]:
    masked = _mask_plate(license_plate)
    logger.info("vehicle lookup requested plate=%s", masked)
    vehicle, error_code = await fetch_vehicle_info(license_plate, masked)
    status = _STATUS_MAP.get(error_code, 200) if error_code else 200
    return vehicle, error_code, status
