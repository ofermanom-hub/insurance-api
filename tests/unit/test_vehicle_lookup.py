from src.core.vehicle_lookup import _mask_plate


def test_mask_plate_7_digits():
    assert _mask_plate("1234567") == "****67"


def test_mask_plate_8_digits():
    assert _mask_plate("12345678") == "****78"


def test_mask_plate_short():
    assert _mask_plate("1") == "****"
