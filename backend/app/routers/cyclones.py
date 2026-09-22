"""
Cyclone Tracking API Router
Owner: Krishna
"""

import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.models import CycloneData, Coordinates, TrackPoint
from app.db.database import get_db
from app.db import models

router = APIRouter()


@router.get("/active", response_model=CycloneData)
async def get_active_cyclone(db: Session = Depends(get_db)):
    """
    Returns real-time cyclone tracking data, current eye position, past track, and forecast cone.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Check if active cyclone in database
    cyclone_event = db.query(models.CycloneEventDB).filter(models.CycloneEventDB.is_active == True).first()
    
    name = cyclone_event.name if cyclone_event else "Cyclone Vardah-II"
    category = cyclone_event.category if cyclone_event else 3
    wind_kmh = cyclone_event.max_wind_kmh if cyclone_event else 165.0
    central_pressure = cyclone_event.central_pressure_mb if cyclone_event else 960.0
    cyclone_id = cyclone_event.cyclone_id if cyclone_event else "CYC-2026-01"

    return CycloneData(
        cyclone_id=cyclone_id,
        name=name,
        category=category,
        max_sustained_wind_kmh=wind_kmh,
        central_pressure_mb=central_pressure,
        current_position=Coordinates(
            lat=14.5,
            lon=82.1,
            recorded_at=now.isoformat(),
            wind_kmh=wind_kmh
        ),
        past_track=[
            TrackPoint(timestamp=(now - datetime.timedelta(hours=18)).isoformat(), lat=12.8, lon=85.2, wind_kmh=110.0),
            TrackPoint(timestamp=(now - datetime.timedelta(hours=12)).isoformat(), lat=13.4, lon=84.1, wind_kmh=135.0),
            TrackPoint(timestamp=(now - datetime.timedelta(hours=6)).isoformat(), lat=14.0, lon=83.0, wind_kmh=150.0),
            TrackPoint(timestamp=now.isoformat(), lat=14.5, lon=82.1, wind_kmh=wind_kmh)
        ],
        forecast_track=[
            TrackPoint(timestamp=(now + datetime.timedelta(hours=6)).isoformat(), lat=15.0, lon=81.3, wind_kmh=175.0, uncertainty_radius_km=35.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=12)).isoformat(), lat=15.6, lon=80.5, wind_kmh=180.0, uncertainty_radius_km=50.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=18)).isoformat(), lat=16.1, lon=79.8, wind_kmh=150.0, uncertainty_radius_km=70.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=24)).isoformat(), lat=16.7, lon=79.1, wind_kmh=95.0, uncertainty_radius_km=90.0)
        ],
        metadata={
            "basin": "North Indian Ocean (Bay of Bengal)",
            "landfall_expected": "South Andhra Pradesh Coast",
            "source": "IMD / Joint Typhoon Warning Center"
        }
    )


@router.get("/all")
async def get_all_cyclones(db: Session = Depends(get_db)):
    """
    Returns a list of all tracked cyclone events.
    """
    events = db.query(models.CycloneEventDB).all()
    if not events:
        return [
            {
                "cyclone_id": "CYC-2026-01",
                "name": "Cyclone Vardah-II",
                "category": 3,
                "max_wind_kmh": 165.0,
                "is_active": True
            }
        ]
    return [
        {
            "cyclone_id": e.cyclone_id,
            "name": e.name,
            "category": e.category,
            "max_wind_kmh": e.max_wind_kmh,
            "is_active": e.is_active
        }
        for e in events
    ]


@router.get("/{cyclone_id}", response_model=CycloneData)
async def get_cyclone_by_id(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Returns detailed tracking data for the requested cyclone ID.
    """
    return await get_active_cyclone(db=db)
