from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from models import Car, get_session
from schemas import CarDetail, CarSummary, CarsListResponse

router = APIRouter(prefix="/api/cars", tags=["cars"])

SortOption = Literal[
    "price_asc", "price_desc", "year_desc", "year_asc",
    "mileage_asc", "mileage_desc", "scraped_at_desc"
]

SORT_COLUMNS: dict[str, object] = {
    "price_asc": Car.price_jpy.asc(),
    "price_desc": Car.price_jpy.desc(),
    "year_desc": Car.year.desc(),
    "year_asc": Car.year.asc(),
    "mileage_asc": Car.mileage_km.asc(),
    "mileage_desc": Car.mileage_km.desc(),
    "scraped_at_desc": Car.scraped_at.desc(),
}


@router.get("", response_model=CarsListResponse)
async def list_cars(
    # Filters
    maker: str | None = Query(None),
    model: str | None = Query(None),
    body_type: str | None = Query(None),
    fuel_type: str | None = Query(None),
    transmission: str | None = Query(None),
    color: str | None = Query(None),
    drive: str | None = Query(None),
    year_min: int | None = Query(None, ge=1900, le=2100),
    year_max: int | None = Query(None, ge=1900, le=2100),
    price_min: int | None = Query(None, ge=0),
    price_max: int | None = Query(None),
    mileage_max: int | None = Query(None, ge=0),
    has_accident: bool | None = Query(None),
    sort: SortOption = Query("scraped_at_desc"),

    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),

    _user: str = Depends(get_current_user),
) -> CarsListResponse:
    async with get_session() as session:
        q = select(Car)

        if maker:
            q = q.where(Car.maker.ilike(f"%{maker}%"))
        if model:
            q = q.where(Car.model.ilike(f"%{model}%"))
        if body_type:
            q = q.where(Car.body_type.ilike(f"%{body_type}%"))
        if fuel_type:
            q = q.where(Car.fuel_type.ilike(f"%{fuel_type}%"))
        if transmission:
            q = q.where(Car.transmission.ilike(f"%{transmission}%"))
        if color:
            q = q.where(Car.color.ilike(f"%{color}%"))
        if drive:
            q = q.where(Car.drive.ilike(f"%{drive}%"))
        if year_min is not None:
            q = q.where(Car.year >= year_min)
        if year_max is not None:
            q = q.where(Car.year <= year_max)
        if price_min is not None:
            q = q.where(Car.price_jpy >= price_min)
        if price_max is not None:
            q = q.where(Car.price_jpy <= price_max)
        if mileage_max is not None:
            q = q.where(Car.mileage_km <= mileage_max)
        if has_accident is not None:
            q = q.where(Car.has_accident == has_accident)

        count_q = select(func.count()).select_from(q.subquery())
        total_result = await session.execute(count_q)
        total = total_result.scalar_one()

        order_col = SORT_COLUMNS.get(sort, Car.scraped_at.desc())
        q = q.order_by(order_col).offset((page - 1) * per_page).limit(per_page)

        result = await session.execute(q)
        cars = result.scalars().all()

        return CarsListResponse(
            total=total,
            page=page,
            per_page=per_page,
            items=[CarSummary.model_validate(c) for c in cars],
        )


@router.get("/{car_id}", response_model=CarDetail)
async def get_car(
    car_id: str,
    _user: str = Depends(get_current_user),
) -> CarDetail:
    from fastapi import HTTPException, status

    async with get_session() as session:
        result = await session.execute(select(Car).where(Car.id == car_id))
        car = result.scalar_one_or_none()
        if not car:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        return CarDetail.model_validate(car)
