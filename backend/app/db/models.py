"""
Database ORM Models
Owner: Krishna
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.db.database import Base


class DistrictDB(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="GREEN")  # RED, ORANGE, YELLOW, GREEN
    flooded_area_sq_km = Column(Float, default=0.0)
    vulnerable_hospitals = Column(Integer, default=0)
    shelters_available = Column(Integer, default=0)
    population_exposed = Column(Integer, default=0)


class HospitalDB(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    district = Column(String(100), index=True, nullable=False)
    beds = Column(Integer, default=50)
    has_backup_power = Column(Boolean, default=True)
    is_coastal = Column(Boolean, default=False)
    status = Column(String(50), default="OPERATIONAL")


class ShelterDB(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    district = Column(String(100), index=True, nullable=False)
    capacity = Column(Integer, default=500)
    current_occupancy = Column(Integer, default=0)
    supplies_days = Column(Integer, default=3)
    status = Column(String(50), default="ACTIVE")


class ActionItemDB(Base):
    __tablename__ = "action_items"

    id = Column(String(50), primary_key=True, index=True)
    cyclone_id = Column(String(50), index=True, nullable=False, default="CYC-2026-01")
    priority = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    phase = Column(String(30), default="PRE_LANDFALL")  # PRE_LANDFALL, LANDFALL, POST_LANDFALL
    sector = Column(String(50), default="Evacuation")
    instruction = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    assigned_agency = Column(String(100), default="NDRF / Local Admin")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CycloneEventDB(Base):
    __tablename__ = "cyclone_events"

    id = Column(Integer, primary_key=True, index=True)
    cyclone_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(Integer, default=1)
    max_wind_kmh = Column(Float, default=100.0)
    central_pressure_mb = Column(Float, default=980.0)
    current_lat = Column(Float, default=0.0)
    current_lon = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
