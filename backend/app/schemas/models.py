"""
Backend Pydantic Data Models & Schemas
Owner: Krishna
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    recorded_at: Optional[str] = None
    wind_kmh: Optional[float] = None


class TrackPoint(BaseModel):
    timestamp: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    wind_kmh: float
    uncertainty_radius_km: Optional[float] = 0.0


class CycloneData(BaseModel):
    cyclone_id: str
    name: str
    category: int
    max_sustained_wind_kmh: float
    central_pressure_mb: Optional[float] = 960.0
    current_position: Coordinates
    past_track: List[TrackPoint] = []
    forecast_track: List[TrackPoint] = []
    metadata: Dict[str, Any] = {}


class DistrictRisk(BaseModel):
    district_name: str
    risk_score: float
    risk_level: str  # RED, ORANGE, YELLOW, GREEN
    flooded_area_sq_km: float
    vulnerable_hospitals: int
    shelters_available: int
    population_exposed: Optional[int] = 0


class ActionItem(BaseModel):
    id: str
    priority: str  # HIGH, MEDIUM, LOW
    phase: str     # PRE_LANDFALL, LANDFALL, POST_LANDFALL
    sector: str    # Evacuation, Medical, Power, Shelter, Rescue
    instruction: str
    status: str    # PENDING, IN_PROGRESS, COMPLETED
    assigned_agency: Optional[str] = "NDRF / District Emergency Operations"


class StatusUpdateRequest(BaseModel):
    action_id: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED


class RiskAssessment(BaseModel):
    cyclone_id: str
    total_population_at_risk: int
    high_risk_districts: List[DistrictRisk]
    executive_summary: str
    threat_level: str
    landfall_eta_hours: int


class LayerInfo(BaseModel):
    name: str
    type: str
    dataset: Optional[str] = None
    tile_url: Optional[str] = None
    opacity: float = 0.75
    status: str = "available"
    reason: Optional[str] = None


class LayerResponse(BaseModel):
    cyclone_id: str
    layers: Dict[str, LayerInfo]


class ConeGeometry(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


class ConeFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: ConeGeometry


class ForecastConeResponse(BaseModel):
    cyclone_id: str
    type: str = "FeatureCollection"
    features: List[ConeFeature]


class HealthResponse(BaseModel):
    status: str
    service: str
    docs: str
    version: str
