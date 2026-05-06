import re

from pydantic import BaseModel, field_validator


class PlateRequest(BaseModel):
    license_plate: str

    @field_validator("license_plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        cleaned = v.strip()
        if not re.fullmatch(r"\d{7,8}", cleaned):
            raise ValueError("License plate must be 7-8 digits")
        return cleaned


class VehicleData(BaseModel):
    license_plate: str
    manufacturer: str
    model: str
    year: str
    color: str
