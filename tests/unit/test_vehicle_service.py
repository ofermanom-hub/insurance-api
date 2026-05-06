from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.integrations.vehicle_service import _parse_upstream_response, fetch_vehicle_info

# --- helpers ---

VALID_RAW = {
    "data": {
        "license_plate": "1234567",
        "manufacturer": "Toyota",
        "model": "Corolla",
        "year": "2020",
        "color": "White",
    }
}


def _mock_http_client(status_code: int, json_data: dict | None = None):
    """Return a patched httpx.AsyncClient that responds with the given status and body."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_cls, mock_client


# --- _parse_upstream_response ---

# Valid upstream payload returns a fully populated vehicle dict
def test_parse_valid_response():
    result = _parse_upstream_response(VALID_RAW)
    assert result is not None
    assert result["license_plate"] == "1234567"
    assert result["manufacturer"] == "Toyota"


# Missing field in data returns None
def test_parse_missing_field():
    raw = {"data": {"license_plate": "1234567", "manufacturer": "Toyota"}}
    assert _parse_upstream_response(raw) is None


# Absent "data" key returns None
def test_parse_no_data_key():
    assert _parse_upstream_response({}) is None


# Completely empty dict returns None
def test_parse_empty_dict():
    assert _parse_upstream_response({}) is None


# --- fetch_vehicle_info ---

# 200 response with valid data returns vehicle dict and no error
async def test_fetch_success():
    mock_cls, _ = _mock_http_client(200, VALID_RAW)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error is None
    assert vehicle["manufacturer"] == "Toyota"


# 200 response with malformed body returns UPSTREAM_MALFORMED
async def test_fetch_malformed_response():
    mock_cls, _ = _mock_http_client(200, {"data": {"bad": "fields"}})
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert vehicle is None
    assert error == "UPSTREAM_MALFORMED"


# 404 returns NOT_FOUND without retrying
async def test_fetch_404():
    mock_cls, mock_client = _mock_http_client(404)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "NOT_FOUND"
    mock_client.post.assert_called_once()


# 401 returns NOT_FOUND without retrying
async def test_fetch_401_no_retry():
    mock_cls, mock_client = _mock_http_client(401)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "NOT_FOUND"
    mock_client.post.assert_called_once()


# 403 returns NOT_FOUND without retrying
async def test_fetch_403_no_retry():
    mock_cls, mock_client = _mock_http_client(403)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "NOT_FOUND"
    mock_client.post.assert_called_once()


# 422 returns NOT_FOUND without retrying
async def test_fetch_422_no_retry():
    mock_cls, mock_client = _mock_http_client(422)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "NOT_FOUND"
    mock_client.post.assert_called_once()


# 500 on first attempt, 200 on second — retries and succeeds
async def test_fetch_retries_on_500_then_succeeds():
    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.json.return_value = VALID_RAW

    err_response = MagicMock()
    err_response.status_code = 500

    mock_client = AsyncMock()
    mock_client.post.side_effect = [err_response, ok_response]

    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error is None
    assert mock_client.post.call_count == 2


# Three consecutive 500s exhaust all retries and return UPSTREAM_UNAVAILABLE
async def test_fetch_all_retries_exhausted():
    mock_cls, mock_client = _mock_http_client(500)
    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "UPSTREAM_UNAVAILABLE"
    assert mock_client.post.call_count == 3


# TimeoutException on every attempt returns UPSTREAM_UNAVAILABLE
async def test_fetch_timeout_exhausts_retries():
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.TimeoutException("timed out")

    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "UPSTREAM_UNAVAILABLE"
    assert mock_client.post.call_count == 3


# ConnectionError on every attempt returns UPSTREAM_UNAVAILABLE
async def test_fetch_connection_error_exhausts_retries():
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.ConnectError("connection refused")

    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error == "UPSTREAM_UNAVAILABLE"


# Timeout then success on second attempt returns vehicle
async def test_fetch_timeout_then_success():
    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.json.return_value = VALID_RAW

    mock_client = AsyncMock()
    mock_client.post.side_effect = [httpx.TimeoutException("timeout"), ok_response]

    mock_cls = MagicMock()
    mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", mock_cls), patch("asyncio.sleep"):
        vehicle, error = await fetch_vehicle_info("1234567")
    assert error is None
    assert vehicle["manufacturer"] == "Toyota"
