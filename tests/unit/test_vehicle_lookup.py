from src.core.utils import mask_plate


def test_mask_plate_7_digits():
    assert mask_plate("1234567") == "****67"


def test_mask_plate_8_digits():
    assert mask_plate("12345678") == "****78"


def test_mask_plate_short():
    assert mask_plate("1") == "****"
