"""
Cyclone Tracking API Router
Owner: Krishna
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.models import CycloneData
from app.db.database import get_db
from app.db import models
from app.services.data_bridge import data_bridge

router = APIRouter()


@router.get("/active", response_model=CycloneData)
async def get_active_cyclone(db: Session = Depends(get_db)):
    """
    Returns real-time cyclone tracking data, current eye position,
    past track, and forecast trajectory.
    """
    # 1. Fetch live or validated tracking model via data bridge
    storm_data = data_bridge.get_cyclone_tracking_data(cyclone_id="CYC-2026-01")

    # 2. Sync / Update DB record
    event = db.query(models.CycloneEventDB).filter(
        models.CycloneEventDB.cyclone_id == storm_data.cyclone_id
    ).first()

    if event:
        event.max_wind_kmh = storm_data.max_sustained_wind_kmh
        event.central_pressure_mb = storm_data.central_pressure_mb
        event.current_lat = storm_data.current_position.lat
        event.current_lon = storm_data.current_position.lon
        try:
            db.commit()
        except Exception:
            db.rollback()

    return storm_data


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
    return data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
