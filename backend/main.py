from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, and_, or_
import os

from models import init_db, Car, get_session
from routers.auth import router as auth_router
from routers.cars import router as cars_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Million Miles API",
    description="Used car listings aggregated from CarSensor.net",
    version="1.0.0",
    lifespan=lifespan,
)

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/cars")
async def get_public_cars(
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    sort_by: str = Query("-scraped_at"),
    # Фильтры
    maker: str | None = Query(None),
    model: str | None = Query(None),
    body_type: str | None = Query(None),
    fuel_type: str | None = Query(None),
    transmission: str | None = Query(None),
    color: str | None = Query(None),
    drive: str | None = Query(None),
    year_min: int | None = Query(None),
    year_max: int | None = Query(None),
    price_min: int | None = Query(None),
    price_max: int | None = Query(None),
    mileage_max: int | None = Query(None),
    has_accident: bool | None = Query(None),
    search: str | None = Query(None),
):
    """
    Публичный эндпоинт для получения списка машин с фильтрацией и поиском.
    """
    async with get_session() as session:
        query = select(Car)
        
        conditions = []
        
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            search_condition = or_(
                Car.maker.ilike(search_term),
                Car.model.ilike(search_term),
                Car.grade.ilike(search_term),
            )
            conditions.append(search_condition)
        
        if maker and maker.strip():
            conditions.append(Car.maker.ilike(f"%{maker.strip()}%"))
        
        if model and model.strip():
            conditions.append(Car.model.ilike(f"%{model.strip()}%"))
        
        if body_type and body_type.strip():
            conditions.append(Car.body_type.ilike(f"%{body_type.strip()}%"))
        
        if fuel_type and fuel_type.strip():
            conditions.append(Car.fuel_type.ilike(f"%{fuel_type.strip()}%"))
        
        if transmission and transmission.strip():
            conditions.append(Car.transmission.ilike(f"%{transmission.strip()}%"))
        
        if color and color.strip():
            conditions.append(Car.color.ilike(f"%{color.strip()}%"))
        
        if drive and drive.strip():
            conditions.append(Car.drive.ilike(f"%{drive.strip()}%"))
        
        if year_min is not None:
            conditions.append(Car.year >= year_min)
        if year_max is not None:
            conditions.append(Car.year <= year_max)
        
        if price_min is not None and price_min > 0:
            conditions.append(Car.price_jpy >= price_min)
        if price_max is not None and price_max > 0:
            conditions.append(Car.price_jpy <= price_max)
        
        if mileage_max is not None:
            conditions.append(Car.mileage_km <= mileage_max)
        
        if has_accident is not None:
            conditions.append(Car.has_accident == has_accident)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar_one()
        
        sort_mapping = {
            "-scraped_at": Car.scraped_at.desc(),
            "scraped_at": Car.scraped_at.asc(),
            "price": Car.price_jpy.asc(),
            "-price": Car.price_jpy.desc(),
            "year": Car.year.asc(),
            "-year": Car.year.desc(),
            "mileage": Car.mileage_km.asc(),
            "-mileage": Car.mileage_km.desc(),
        }
        order_by = sort_mapping.get(sort_by, Car.scraped_at.desc())
        query = query.order_by(order_by)
        
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        cars = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "per_page": limit,
            "items": [
                {
                    "id": str(c.id),
                    "source_id": c.source_id,
                    "source_url": c.source_url,
                    "maker": c.maker,
                    "model": c.model,
                    "grade": c.grade,
                    "year": c.year,
                    "mileage_km": c.mileage_km,
                    "price_jpy": c.price_jpy,
                    "total_price_jpy": c.total_price_jpy,
                    "color": c.color,
                    "fuel_type": c.fuel_type,
                    "transmission": c.transmission,
                    "body_type": c.body_type,
                    "drive": c.drive,
                    "location": c.location,
                    "shop_name": c.shop_name,
                    "image_url": c.images[0] if c.images else None,
                    "images": c.images or [],
                    "scraped_at": c.scraped_at.isoformat() if c.scraped_at else None,
                }
                for c in cars
            ]
        }


@app.get("/cars/{car_id}")
async def get_public_car(car_id: str):
    async with get_session() as session:
        result = await session.execute(select(Car).where(Car.id == car_id))
        car = result.scalar_one_or_none()
        
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car not found"
            )
        
        return {
            "id": str(car.id),
            "source_id": car.source_id,
            "source_url": car.source_url,
            "maker": car.maker,
            "model": car.model,
            "grade": car.grade,
            "year": car.year,
            "mileage_km": car.mileage_km,
            "price_jpy": car.price_jpy,
            "total_price_jpy": car.total_price_jpy,
            "color": car.color,
            "fuel_type": car.fuel_type,
            "transmission": car.transmission,
            "body_type": car.body_type,
            "displacement_cc": car.displacement_cc,
            "drive": car.drive,
            "doors": car.doors,
            "seats": car.seats,
            "condition_score": car.condition_score,
            "has_accident": car.has_accident,
            "location": car.location,
            "shop_name": car.shop_name,
            "images": car.images or [],
            "equipment": car.equipment or {},
            "scraped_at": car.scraped_at.isoformat() if car.scraped_at else None,
        }


app.include_router(auth_router)
app.include_router(cars_router)


@app.get("/")
async def root():
    return {
        "message": "Million Miles API",
        "docs": "/docs",
        "endpoints": {
            "public_cars": "/cars",
            "public_car_detail": "/cars/{car_id}",
            "auth": "/api/auth/token",
            "private_cars": "/api/cars",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}