from unittest.mock import AsyncMock, patch

import pytest

from src.core.utils import mask_plate
from src.core.vehicle_lookup import lookup_vehicle

# --- mask_plate ---

# 7-digit plate exposes only last 2 digits
def test_mask_plate_7_digits():
    assert mask_plate("1234567") == "****67"


# 8-digit plate exposes only last 2 digits
def test_mask_plate_8_digits():
    assert mask_plate("12345678") == "****78"


# Single-digit plate returns full mask
def test_mask_plate_short():
    assert mask_plate("1") == "****"


# Empty string returns full mask
def test_mask_plate_empty():
    assert mask_plate("") == "****"


# Exactly 2 digits exposes both
def test_mask_plate_two_digits():
    assert mask_plate("12") == "****12"


# --- lookup_vehicle ---

VEHICLE = {
    "license_plate": "1234567",
    "manufacturer": "Toyota",
    "model": "Corolla",
    "year": "2020",
    "color": "White",
}


# Successful lookup returns vehicle data, no error, and HTTP 200
async def test_lookup_vehicle_success():
    with patch("src.core.vehicle_lookup.fetch_vehicle_info", new_callable=AsyncMock) as mock:
        mock.return_value = (VEHICLE, None)
        vehicle, error_code, status = await lookup_vehicle("1234567")
    assert vehicle == VEHICLE
    assert error_code is None
    assert status == 200


# NOT_FOUND error maps to HTTP 404
async def test_lookup_vehicle_not_found():
    with patch("src.core.vehicle_lookup.fetch_vehicle_info", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "NOT_FOUND")
        vehicle, error_code, status = await lookup_vehicle("1234567")
    assert vehicle is None
    assert error_code == "NOT_FOUND"
    assert status == 404


# UPSTREAM_MALFORMED error maps to HTTP 502
async def test_lookup_vehicle_upstream_malformed():
    with patch("src.core.vehicle_lookup.fetch_vehicle_info", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "UPSTREAM_MALFORMED")
        vehicle, error_code, status = await lookup_vehicle("1234567")
    assert error_code == "UPSTREAM_MALFORMED"
    assert status == 502


# UPSTREAM_UNAVAILABLE error maps to HTTP 503
async def test_lookup_vehicle_upstream_unavailable():
    with patch("src.core.vehicle_lookup.fetch_vehicle_info", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "UPSTREAM_UNAVAILABLE")
        vehicle, error_code, status = await lookup_vehicle("1234567")
    assert error_code == "UPSTREAM_UNAVAILABLE"
    assert status == 503


# Unknown error code falls back to HTTP 500
async def test_lookup_vehicle_unknown_error_code():
    with patch("src.core.vehicle_lookup.fetch_vehicle_info", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "SOME_NEW_ERROR")
        vehicle, error_code, status = await lookup_vehicle("1234567")
    assert error_code == "SOME_NEW_ERROR"
    assert status == 500
