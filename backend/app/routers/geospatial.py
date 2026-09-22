"""
Geospatial Layers & Map Tile API Router
Owner: Krishna (Bridging GEE Raster & Vector Feeds)
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.schemas.models import LayerResponse, LayerInfo, ForecastConeResponse, ConeFeature, ConeGeometry

router = APIRouter()


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
                dataset="COPERNICUS/S1_GRD",
                tile_url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
                opacity=0.75,
                status="available"
            ),
            "gpm_rainfall": LayerInfo(
                name="GPM 24-Hr Precipitation Heatmap",
                type="raster_tile",
                dataset="NASA/GPM_L3/IMERG_V07",
                tile_url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                opacity=0.6,
                status="available"
            )
        }
    )


@router.get("/cone/{cyclone_id}", response_model=ForecastConeResponse)
async def get_forecast_cone(cyclone_id: str = "CYC-2026-01"):
    """
    Returns GeoJSON polygon geometry representing the cone of uncertainty for the cyclone forecast.
    """
    # 72-hour forecast uncertainty cone polygon along south Andhra coastline
    cone_polygon = [
        [
            [82.1, 14.5],
            [81.8, 14.8],
            [81.2, 15.3],
            [80.3, 15.9],
            [79.4, 16.5],
            [78.7, 17.1],
            [79.5, 16.9],
            [80.7, 16.3],
            [81.6, 15.7],
            [82.3, 15.1],
            [82.1, 14.5]
        ]
    ]

    return ForecastConeResponse(
        cyclone_id=cyclone_id,
        type="FeatureCollection",
        features=[
            ConeFeature(
                type="Feature",
                properties={
                    "cyclone_id": cyclone_id,
                    "description": "72-Hour Cone of Uncertainty (Cat 3 Track)",
                    "max_wind_radius_km": 90.0,
                    "confidence_interval": "67%"
                },
                geometry=ConeGeometry(
                    type="Polygon",
                    coordinates=cone_polygon
                )
            )
        ]
    )
