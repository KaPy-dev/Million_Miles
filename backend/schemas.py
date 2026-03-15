from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CarSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_url: str
    maker: str | None
    model: str | None
    grade: str | None
    year: int | None
    mileage_km: int | None
    price_jpy: int | None
    total_price_jpy: int | None
    color: str | None
    fuel_type: str | None
    transmission: str | None
    body_type: str | None
    condition_score: float | None
    has_accident: bool | None
    location: str | None
    images: list[Any] | None
    scraped_at: datetime


class CarDetail(CarSummary):
    displacement_cc: int | None
    drive: str | None
    doors: int | None
    seats: int | None
    shop_name: str | None
    equipment: dict[str, Any] | None
    raw_data: dict[str, Any] | None


class CarsListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[CarSummary]
