"""
Database configuration and connection management
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.core.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # GDPR fields
    data_processing_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    consent_date = Column(DateTime(timezone=True))


class Property(Base):
    """Property/Location model"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    property_type = Column(String)  # residential, commercial, agricultural
    size_sqm = Column(Float)
    construction_year = Column(Integer)
    infrastructure_details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClimateData(Base):
    """Climate data model"""
    __tablename__ = "climate_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, index=True, nullable=False)
    data_source = Column(String, nullable=False)  # API source
    data_type = Column(String, nullable=False)  # temperature, precipitation, etc.
    value = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Analysis(Base):
    """Climate analysis results model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    property_id = Column(Integer, index=True, nullable=False)
    analysis_type = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    results = Column(JSON)
    risk_score = Column(Float)
    confidence_level = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Recommendation(Base):
    """AI-generated recommendations model"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, index=True, nullable=False)
    category = Column(String, nullable=False)  # adaptation, mitigation, emergency
    title = Column(String, nullable=False)
    description = Column(Text)
    priority_level = Column(String)  # low, medium, high, critical
    estimated_cost = Column(Float)
    implementation_timeline = Column(String)
    effectiveness_score = Column(Float)
    resources_required = Column(JSON)
    implementation_steps = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """GDPR compliance audit log"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String, nullable=False)
    resource = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class DataRetention(Base):
    """Data retention tracking for GDPR compliance"""
    __tablename__ = "data_retention"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    data_type = Column(String, nullable=False)
    retention_until = Column(DateTime(timezone=True), nullable=False)
    anonymized = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
