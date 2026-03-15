from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    pool_recycle=3600,  
    pool_size=10,       
    max_overflow=20    
)

class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (UniqueConstraint("source_id", name="uq_cars_source_id"),)

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)

    maker: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(200))
    grade: Mapped[str | None] = mapped_column(String(300))
    year: Mapped[int | None] = mapped_column(Integer)
    mileage_km: Mapped[int | None] = mapped_column(Integer)
    price_jpy: Mapped[int | None] = mapped_column(Integer)
    total_price_jpy: Mapped[int | None] = mapped_column(Integer)
    color: Mapped[str | None] = mapped_column(String(100))
    fuel_type: Mapped[str | None] = mapped_column(String(100))
    transmission: Mapped[str | None] = mapped_column(String(50))
    body_type: Mapped[str | None] = mapped_column(String(100))
    displacement_cc: Mapped[int | None] = mapped_column(Integer)
    drive: Mapped[str | None] = mapped_column(String(50))
    doors: Mapped[int | None] = mapped_column(Integer)
    seats: Mapped[int | None] = mapped_column(Integer)
    condition_score: Mapped[float | None] = mapped_column(Float)
    has_accident: Mapped[bool | None] = mapped_column(Boolean)
    location: Mapped[str | None] = mapped_column(String(100))
    shop_name: Mapped[str | None] = mapped_column(String(200))

    images: Mapped[list | None] = mapped_column(JSONB, default=list)
    equipment: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session() -> AsyncSession:
    return AsyncSession(engine, expire_on_commit=False)