import pytest
from pydantic import ValidationError
from src.models.vehicle import PlateRequest


def test_valid_7_digit_plate():
    assert PlateRequest(license_plate="1234567").license_plate == "1234567"


def test_valid_8_digit_plate():
    assert PlateRequest(license_plate="12345678").license_plate == "12345678"


def test_strips_whitespace():
    assert PlateRequest(license_plate="  1234567  ").license_plate == "1234567"


def test_invalid_non_digits():
    with pytest.raises(ValidationError):
        PlateRequest(license_plate="ABC1234")


def test_invalid_too_short():
    with pytest.raises(ValidationError):
        PlateRequest(license_plate="123456")
