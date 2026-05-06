import asyncio
import logging

import httpx

from src.config.settings import MAX_RETRIES, TIMEOUT_SECONDS, UPSTREAM_URL
from src.models.vehicle import VehicleData

logger = logging.getLogger("insurance_api.integrations.vehicle_service")


def _parse_upstream_response(raw: dict) -> dict | None:
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


async def fetch_vehicle_info(license_plate: str, masked: str) -> tuple[dict | None, str | None]:
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                r = await client.post(UPSTREAM_URL, json={"license_plate": license_plate})

            if r.status_code == 200:
                raw = r.json()
                vehicle = _parse_upstream_response(raw)
                if vehicle is None:
                    logger.error("upstream response malformed plate=%s body=%s", masked, raw)
                    return None, "UPSTREAM_MALFORMED"
                logger.info("vehicle found plate=%s manufacturer=%s", masked, vehicle["manufacturer"])
                return vehicle, None

            if r.status_code == 404:
                logger.info("vehicle not found plate=%s", masked)
                return None, "NOT_FOUND"

            logger.warning(
                "upstream unexpected status plate=%s status=%d attempt=%d",
                masked, r.status_code, attempt + 1,
            )

        except httpx.TimeoutException:
            logger.warning("upstream timeout plate=%s attempt=%d/%d", masked, attempt + 1, MAX_RETRIES)

        except httpx.RequestError as exc:
            logger.warning(
                "upstream connection error plate=%s attempt=%d/%d error=%s",
                masked, attempt + 1, MAX_RETRIES, type(exc).__name__,
            )

        if attempt < MAX_RETRIES - 1:
            backoff = 0.5 * (attempt + 1)
            logger.info("retrying after %.1fs", backoff)
            await asyncio.sleep(backoff)

    logger.error("all retries exhausted plate=%s", masked)
    return None, "UPSTREAM_UNAVAILABLE"
