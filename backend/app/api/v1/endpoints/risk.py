"""
Risk & Exposure Assessment Endpoints
Owner: Krishna
"""

from fastapi import APIRouter
from app.models.schemas import RiskAssessment
from app.services.risk_engine import risk_engine

router = APIRouter()


@router.get("/exposure/{cyclone_id}", response_model=RiskAssessment)
async def get_cyclone_exposure(cyclone_id: str):
    """
    Computes and returns population exposure, vulnerable infrastructure,
    and composite risk index for the selected cyclone.
    """
    return risk_engine.calculate_exposure(cyclone_id=cyclone_id, wind_speed=165.0, flooded_area=142.5)
