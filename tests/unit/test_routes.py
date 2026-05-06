from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

VEHICLE = {
    "license_plate": "1234567",
    "manufacturer": "Toyota",
    "model": "Corolla",
    "year": "2020",
    "color": "White",
}


# GET /health always returns 200 with status ok
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Valid plate with a found vehicle returns 200 and vehicle data
def test_vehicle_info_success():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (VEHICLE, None, 200)
        response = client.post("/vehicle-info", json={"license_plate": "1234567"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == VEHICLE


# Valid plate that is not in the system returns 404 with NOT_FOUND code
def test_vehicle_info_not_found():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "NOT_FOUND", 404)
        response = client.post("/vehicle-info", json={"license_plate": "1234567"})
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Vehicle not found"


# Malformed upstream response returns 502 with UPSTREAM_MALFORMED code
def test_vehicle_info_upstream_malformed():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "UPSTREAM_MALFORMED", 502)
        response = client.post("/vehicle-info", json={"license_plate": "1234567"})
    assert response.status_code == 502
    body = response.json()
    assert body["error"]["code"] == "UPSTREAM_MALFORMED"


# Upstream service down returns 503 with UPSTREAM_UNAVAILABLE code
def test_vehicle_info_upstream_unavailable():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "UPSTREAM_UNAVAILABLE", 503)
        response = client.post("/vehicle-info", json={"license_plate": "1234567"})
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "UPSTREAM_UNAVAILABLE"


# Plate with letters is rejected at validation with 422
def test_vehicle_info_invalid_plate_letters():
    response = client.post("/vehicle-info", json={"license_plate": "ABC1234"})
    assert response.status_code == 422


# Plate shorter than 7 digits is rejected with 422
def test_vehicle_info_plate_too_short():
    response = client.post("/vehicle-info", json={"license_plate": "123456"})
    assert response.status_code == 422


# Plate longer than 8 digits is rejected with 422
def test_vehicle_info_plate_too_long():
    response = client.post("/vehicle-info", json={"license_plate": "123456789"})
    assert response.status_code == 422


# Empty string plate is rejected with 422
def test_vehicle_info_empty_plate():
    response = client.post("/vehicle-info", json={"license_plate": ""})
    assert response.status_code == 422


# Missing license_plate field is rejected with 422
def test_vehicle_info_missing_field():
    response = client.post("/vehicle-info", json={})
    assert response.status_code == 422


# Plate with surrounding whitespace is stripped and accepted
def test_vehicle_info_strips_whitespace():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (VEHICLE, None, 200)
        response = client.post("/vehicle-info", json={"license_plate": "  1234567  "})
    assert response.status_code == 200


# Unknown error code falls back to "Unknown error" message
def test_vehicle_info_unknown_error_message():
    with patch("src.api.routes.lookup_vehicle", new_callable=AsyncMock) as mock:
        mock.return_value = (None, "SOME_NEW_ERROR", 500)
        response = client.post("/vehicle-info", json={"license_plate": "1234567"})
    assert response.json()["error"]["message"] == "Unknown error"
