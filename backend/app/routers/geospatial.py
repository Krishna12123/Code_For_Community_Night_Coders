"""
Geospatial Layers, Cone of Uncertainty & Wind Buffer API Router
Owner: Krishna (Bridging GEE Raster & Vector Feeds)
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.schemas.models import (
    LayerResponse,
    ForecastConeResponse,
    WindBufferResponse
)
from app.services.data_bridge import data_bridge
from app.services.geometry_engine import geometry_engine

router = APIRouter()


@router.get("/layers", response_model=LayerResponse)
async def get_geospatial_layers(cyclone_id: str = "CYC-2026-01"):
    """
    Returns active Google Earth Engine (GEE) map tile layer endpoints
    (Sentinel-1 SAR flood inundation & NASA GPM rainfall accumulation).
    """
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    lat = storm.current_position.lat if storm else 14.5
    lon = storm.current_position.lon if storm else 82.1
    return data_bridge.get_gee_layers(cyclone_id=cyclone_id, lat=lat, lon=lon)


@router.get("/cone/{cyclone_id}", response_model=ForecastConeResponse)
async def get_forecast_cone(cyclone_id: str = "CYC-2026-01"):
    """
    Generates dynamic GeoJSON polygon geometry representing the cone of uncertainty
    for the cyclone forecast based on trajectory points and uncertainty radii.
    """
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    
    track_points = []
    if storm:
        # Include current position as root of the cone
        track_points.append({
            "lat": storm.current_position.lat,
            "lon": storm.current_position.lon,
            "uncertainty_radius_km": 15.0
        })
        for pt in storm.forecast_track:
            track_points.append({
                "lat": pt.lat,
                "lon": pt.lon,
                "uncertainty_radius_km": pt.uncertainty_radius_km or 35.0
            })

    return geometry_engine.generate_cone_of_uncertainty(
        cyclone_id=cyclone_id,
        track_points=track_points
    )


@router.get("/wind-buffers/{cyclone_id}", response_model=WindBufferResponse)
async def get_wind_hazard_buffers(cyclone_id: str = "CYC-2026-01"):
    """
    Returns multi-tier concentric wind hazard buffers:
    - 34-knot (Gale force, 63 km/h+)
    - 50-knot (Storm force, 92 km/h+)
    - 64-knot (Hurricane force, 118 km/h+)
    """
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    lat = storm.current_position.lat if storm else 14.5
    lon = storm.current_position.lon if storm else 82.1
    wind = storm.max_sustained_wind_kmh if storm else 165.0

    return geometry_engine.generate_wind_buffers(
        cyclone_id=cyclone_id,
        current_lat=lat,
        current_lon=lon,
        max_wind_kmh=wind
    )
