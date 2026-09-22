"""
Database Connection and Session Management
Owner: Krishna
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Setup SQLite or PostgreSQL engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates database tables and populates baseline spatial seed data if empty.
    """
    from app.db import models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if districts already seeded
        if db.query(models.DistrictDB).count() == 0:
            seed_districts = [
                models.DistrictDB(
                    name="Nellore",
                    risk_score=89.5,
                    risk_level="RED",
                    flooded_area_sq_km=142.5,
                    vulnerable_hospitals=8,
                    shelters_available=42,
                    population_exposed=620000
                ),
                models.DistrictDB(
                    name="Prakasam",
                    risk_score=81.0,
                    risk_level="RED",
                    flooded_area_sq_km=98.0,
                    vulnerable_hospitals=5,
                    shelters_available=30,
                    population_exposed=540000
                ),
                models.DistrictDB(
                    name="Bapatla",
                    risk_score=68.4,
                    risk_level="ORANGE",
                    flooded_area_sq_km=54.2,
                    vulnerable_hospitals=3,
                    shelters_available=25,
                    population_exposed=410000
                ),
                models.DistrictDB(
                    name="Krishna",
                    risk_score=45.0,
                    risk_level="YELLOW",
                    flooded_area_sq_km=21.0,
                    vulnerable_hospitals=2,
                    shelters_available=38,
                    population_exposed=280000
                )
            ]
            db.add_all(seed_districts)

        # Check if actions already seeded
        if db.query(models.ActionItemDB).count() == 0:
            seed_actions = [
                models.ActionItemDB(
                    id="ACT-001",
                    cyclone_id="CYC-2026-01",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Evacuation",
                    instruction="Evacuate 45,000 residents from low-lying coastal villages (0-5km) in Nellore.",
                    status="IN_PROGRESS",
                    assigned_agency="NDRF Battalion 10 & District Revenue"
                ),
                models.ActionItemDB(
                    id="ACT-002",
                    cyclone_id="CYC-2026-01",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Medical",
                    instruction="Deliver diesel generator backup & oxygen supplies to 8 high-risk hospitals.",
                    status="COMPLETED",
                    assigned_agency="District Medical & Health Office"
                ),
                models.ActionItemDB(
                    id="ACT-003",
                    cyclone_id="CYC-2026-01",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Shelter",
                    instruction="Activate 42 cyclone relief shelters with 72-hour dry food and potable water supplies.",
                    status="IN_PROGRESS",
                    assigned_agency="Civil Supplies & SDRF"
                ),
                models.ActionItemDB(
                    id="ACT-004",
                    cyclone_id="CYC-2026-01",
                    priority="MEDIUM",
                    phase="LANDFALL",
                    sector="Power",
                    instruction="Pre-emptively shut down secondary electrical grids in vulnerable storm-surge zones.",
                    status="PENDING",
                    assigned_agency="State Electricity Distribution Company"
                ),
                models.ActionItemDB(
                    id="ACT-005",
                    cyclone_id="CYC-2026-01",
                    priority="MEDIUM",
                    phase="POST_LANDFALL",
                    sector="Rescue",
                    instruction="Deploy 12 NDRF search and rescue boat teams along coastal river mouths.",
                    status="PENDING",
                    assigned_agency="NDRF & Indian Coast Guard"
                )
            ]
            db.add_all(seed_actions)

        # Check if active cyclone record exists
        if db.query(models.CycloneEventDB).count() == 0:
            active_event = models.CycloneEventDB(
                cyclone_id="CYC-2026-01",
                name="Cyclone Vardah-II",
                category=3,
                max_wind_kmh=165.0,
                central_pressure_mb=960.0,
                current_lat=14.5,
                current_lon=82.1,
                is_active=True
            )
            db.add(active_event)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB Init Warning] Error seeding database: {e}")
    finally:
        db.close()
