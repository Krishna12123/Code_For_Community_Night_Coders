"""
Backend Pydantic Data Models & Schemas
Owner: Krishna
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float
    recorded_at: Optional[str] = None


class TrackPoint(BaseModel):
    timestamp: str
    lat: float
    lon: float
    wind_kmh: float
    uncertainty_radius_km: Optional[float] = 0.0


class CycloneData(BaseModel):
    cyclone_id: str
    name: str
    category: int
    max_sustained_wind_kmh: float
    central_pressure_mb: float
    current_position: Coordinates
    past_track: List[TrackPoint]
    forecast_track: List[TrackPoint]


class DistrictRisk(BaseModel):
    district_name: str
    risk_score: float
    risk_level: str  # RED, ORANGE, YELLOW, GREEN
    flooded_area_sq_km: float
    vulnerable_hospitals: int
    shelters_available: int


class ActionItem(BaseModel):
    id: str
    priority: str  # HIGH, MEDIUM, LOW
    phase: str     # PRE_LANDFALL, LANDFALL, POST_LANDFALL
    sector: str    # Evacuation, Medical, Power, Shelter, Rescue
    instruction: str
    status: str    # PENDING, IN_PROGRESS, COMPLETED


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
    tile_url: str
    opacity: float


class LayerResponse(BaseModel):
    cyclone_id: str
    layers: Dict[str, LayerInfo]
