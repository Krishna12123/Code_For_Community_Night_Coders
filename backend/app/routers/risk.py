"""
Risk & Exposure Assessment API Router
Owner: Krishna (Backend & Risk Engine Architect)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.models import RiskAssessment, DistrictRisk
from app.db.database import get_db
from app.services.risk_engine import risk_engine
from app.services.data_bridge import data_bridge

router = APIRouter()


@router.get("/exposure/{cyclone_id}", response_model=RiskAssessment)
async def get_cyclone_exposure(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Computes and returns population exposure, vulnerable infrastructure,
    and composite multi-hazard risk index for the selected cyclone.
    """
    # 1. Fetch active storm coordinates & wind speed
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    storm_lat = storm.current_position.lat if storm else 14.5
    storm_lon = storm.current_position.lon if storm else 82.1
    max_wind = storm.max_sustained_wind_kmh if storm else 165.0

    # 2. Compute dynamic spatial exposure and composite multi-hazard score
    assessment = risk_engine.calculate_exposure_from_db(
        db=db,
        cyclone_id=cyclone_id,
        storm_lat=storm_lat,
        storm_lon=storm_lon,
        max_wind_kmh=max_wind
    )

    return assessment


@router.get("/districts/{cyclone_id}", response_model=List[DistrictRisk])
async def get_district_risk_breakdown(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Returns district-wise composite risk scores, flood zones, and infrastructure vulnerability.
    """
    assessment = await get_cyclone_exposure(cyclone_id=cyclone_id, db=db)
    return assessment.high_risk_districts
