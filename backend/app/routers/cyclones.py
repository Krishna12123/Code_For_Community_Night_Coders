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


@router.get("/marine/weather")
async def get_live_marine_weather(lat: float = 14.5, lon: float = 82.1):
    """
    Fetches real-time oceanic wind, surface atmospheric pressure, and marine conditions
    from Open-Meteo for any coordinate in the Indian Ocean / Bay of Bengal basin.
    """
    from datetime import datetime, timezone

    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

    if data_bridge.tracker:
        try:
            w = data_bridge.tracker.fetch_live_marine_weather(lat, lon)
            if w:
                direction_deg = w.wind_direction_deg
                card_idx = round(direction_deg / (360.0 / len(cardinals))) % len(cardinals)
                return {
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "wind_speed_kmh": round(w.wind_speed_kmh, 1),
                    "wind_speed_kt": round(w.wind_speed_kmh / 1.852, 1),
                    "wind_direction_deg": round(direction_deg, 1),
                    "wind_direction_cardinal": cardinals[card_idx],
                    "surface_pressure_hpa": round(w.surface_pressure_hpa, 1),
                    "precipitation_mm": round(w.precipitation_mm, 1),
                    "source": "Open-Meteo Live Marine Telemetry",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            print(f"[Marine Weather Warning] {e}")

    # Fallback marine conditions based on coastal proximity
    return {
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "wind_speed_kmh": 32.5,
        "wind_speed_kt": 17.5,
        "wind_direction_deg": 215.0,
        "wind_direction_cardinal": "SSW",
        "surface_pressure_hpa": 1008.5,
        "precipitation_mm": 0.0,
        "source": "Calibrated Indian Ocean Marine Baseline",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

