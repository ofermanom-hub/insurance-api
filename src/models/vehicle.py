import re

from pydantic import BaseModel, Field, field_validator


class PlateRequest(BaseModel):
    license_plate: str = Field(min_length=7, max_length=8)

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
