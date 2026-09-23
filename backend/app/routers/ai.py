"""
Gemini AI Disaster Briefing API Router
Owner: Krishna (Bridging AI reasoning from Vikash's domain to REST API)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.models import AIBriefingResponse
from app.db.database import get_db
from app.services.risk_engine import risk_engine
from app.services.data_bridge import data_bridge

router = APIRouter()


@router.get("/briefing/{cyclone_id}", response_model=AIBriefingResponse)
async def get_ai_disaster_briefing(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Executes Gemini AI reasoning to generate executive disaster situation reports,
    district risk summaries, and emergency mitigation advice based on real-time evidence.
    """
    # 1. Fetch active exposure metrics to provide ground truth context to Gemini
    risk_assessment = risk_engine.calculate_exposure_from_db(
        db=db,
        cyclone_id=cyclone_id
    )

    exposure_summary = {
        "total_population_at_risk": risk_assessment.total_population_at_risk,
        "threat_level": risk_assessment.threat_level,
        "high_risk_districts": [
            {
                "name": d.district_name,
                "risk_score": d.risk_score,
                "risk_level": d.risk_level,
                "flooded_area_sq_km": d.flooded_area_sq_km,
                "vulnerable_hospitals": d.vulnerable_hospitals
            }
            for d in risk_assessment.high_risk_districts
        ]
    }

    # 2. Call Data Bridge to run Gemini reasoning engine
    briefing = data_bridge.get_ai_situation_briefing(
        cyclone_id=cyclone_id,
        exposure_summary=exposure_summary
    )

    return briefing
