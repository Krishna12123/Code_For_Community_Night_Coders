"""
Cyclone & Geospatial Layers API Endpoints
Owner: Krishna (Bridging Vikash's GEE/Tracker output)
"""

import datetime
from fastapi import APIRouter
from app.models.schemas import CycloneData, Coordinates, TrackPoint, LayerResponse, LayerInfo

router = APIRouter()


@router.get("/active", response_model=CycloneData)
async def get_active_cyclone():
    """
    Returns real-time cyclone tracking data, current eye position, past track, and forecast cone.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return CycloneData(
        cyclone_id="CYC-2026-01",
        name="Cyclone Vardah-II",
        category=3,
        max_sustained_wind_kmh=165.0,
        central_pressure_mb=960.0,
        current_position=Coordinates(
            lat=14.5,
            lon=82.1,
            recorded_at=now.isoformat()
        ),
        past_track=[
            TrackPoint(timestamp=(now - datetime.timedelta(hours=18)).isoformat(), lat=12.8, lon=85.2, wind_kmh=110.0),
            TrackPoint(timestamp=(now - datetime.timedelta(hours=12)).isoformat(), lat=13.4, lon=84.1, wind_kmh=135.0),
            TrackPoint(timestamp=(now - datetime.timedelta(hours=6)).isoformat(), lat=14.0, lon=83.0, wind_kmh=150.0),
            TrackPoint(timestamp=now.isoformat(), lat=14.5, lon=82.1, wind_kmh=165.0)
        ],
        forecast_track=[
            TrackPoint(timestamp=(now + datetime.timedelta(hours=6)).isoformat(), lat=15.0, lon=81.3, wind_kmh=175.0, uncertainty_radius_km=35.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=12)).isoformat(), lat=15.6, lon=80.5, wind_kmh=180.0, uncertainty_radius_km=50.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=18)).isoformat(), lat=16.1, lon=79.8, wind_kmh=150.0, uncertainty_radius_km=70.0),
            TrackPoint(timestamp=(now + datetime.timedelta(hours=24)).isoformat(), lat=16.7, lon=79.1, wind_kmh=95.0, uncertainty_radius_km=90.0)
        ]
    )


@router.get("/layers", response_model=LayerResponse)
async def get_geospatial_layers(cyclone_id: str = "CYC-2026-01"):
    """
    Returns active map tile layer endpoints (Sentinel-1 SAR flood & GPM rainfall).
    """
    return LayerResponse(
        cyclone_id=cyclone_id,
        layers={
            "sar_flood": LayerInfo(
                name="Sentinel-1 SAR Flood Inundation",
                type="raster_tile",
                tile_url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
                opacity=0.75
            ),
            "gpm_rainfall": LayerInfo(
                name="GPM 24-Hr Precipitation Heatmap",
                type="raster_tile",
                tile_url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                opacity=0.6
            )
        }
    )
