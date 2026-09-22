from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class Point(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    recorded_at: datetime
    wind_kmh: Optional[float] = None
    uncertainty_radius_km: Optional[float] = None

class CycloneData(BaseModel):
    cyclone_id: str
    name: str
    source: Literal["live", "synthetic_fixture"]
    category: int
    max_sustained_wind_kmh: float
    central_pressure_mb: Optional[float] = None
    current_position: Point
    past_track: List[Point] = []
    forecast_track: List[Point] = []
    metadata: Dict[str, Any] = {}

class WeatherData(BaseModel):
    source: Literal["live", "mock_fixture"]
    wind_speed_kmh: float
    wind_direction_deg: float
    surface_pressure_hpa: float
    precipitation_mm: float

class LayerInfo(BaseModel):
    dataset: str
    status: Literal["available", "unavailable"]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    accumulation_mm: Optional[float] = None
    tile_url: Optional[str] = None
    reason: Optional[str] = None

class GeospatialEvidence(BaseModel):
    analysis_region: Dict[str, Any]
    rainfall: LayerInfo
    flood: LayerInfo
    generated_at: datetime

class Action(BaseModel):
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    phase: Literal["PRE_LANDFALL", "LANDFALL", "POST_LANDFALL"]
    sector: str
    instruction: str

class AdvisoryBriefing(BaseModel):
    executive_summary: str
    threat_level: Literal["RED", "ORANGE", "YELLOW", "GREEN", "UNKNOWN"]
    high_risk_districts: List[str]
    critical_actions: List[Action]
    evidence_used: List[str] = []
    limitations: List[str] = []
    mode: Literal["live", "demo_fixture"] = "live"
