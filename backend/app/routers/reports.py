"""
Reports API Router - PDF & JSON Disaster Situation Report Generation
Owner: Krishna (Backend & Risk Engine Architect)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.risk_engine import risk_engine
from app.services.action_engine import action_engine
from app.services.data_bridge import data_bridge
from app.services.report_engine import report_engine

router = APIRouter()


@router.get("/situation-report/pdf/{cyclone_id}")
async def get_situation_report_pdf(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Generates and returns an official, multi-page downloadable PDF Situation Report (SITREP)
    combining storm telemetry, GEE satellite flood evidence, district risk scoring,
    Gemini AI briefings, and operational SOP actions.
    """
    # 1. Fetch storm data
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    lat = storm.current_position.lat if storm else 14.5
    lon = storm.current_position.lon if storm else 82.1
    wind = storm.max_sustained_wind_kmh if storm else 165.0

    # 2. Fetch risk assessment
    risk_assessment = risk_engine.calculate_exposure_from_db(
        db=db,
        cyclone_id=cyclone_id,
        storm_lat=lat,
        storm_lon=lon,
        max_wind_kmh=wind
    )

    # 3. Fetch actions
    red_districts = [d.district_name for d in risk_assessment.high_risk_districts if d.risk_level == "RED"]
    actions = action_engine.get_or_create_actions_for_cyclone(
        db=db,
        cyclone_id=cyclone_id,
        threat_level=risk_assessment.threat_level,
        red_districts=red_districts
    )

    # 4. Fetch AI Briefing
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
    ai_briefing = data_bridge.get_ai_situation_briefing(
        cyclone_id=cyclone_id,
        exposure_summary=exposure_summary
    )

    # 5. Generate PDF bytes
    pdf_bytes = report_engine.generate_pdf_report(
        cyclone_id=cyclone_id,
        storm_data=storm,
        risk_assessment=risk_assessment,
        ai_briefing=ai_briefing,
        actions=actions
    )

    filename = f"Situation_Report_{cyclone_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/situation-report/json/{cyclone_id}")
async def get_situation_report_json(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Returns consolidated Situation Report payload in structured JSON format.
    """
    storm = data_bridge.get_cyclone_tracking_data(cyclone_id=cyclone_id)
    lat = storm.current_position.lat if storm else 14.5
    lon = storm.current_position.lon if storm else 82.1
    wind = storm.max_sustained_wind_kmh if storm else 165.0

    risk_assessment = risk_engine.calculate_exposure_from_db(
        db=db,
        cyclone_id=cyclone_id,
        storm_lat=lat,
        storm_lon=lon,
        max_wind_kmh=wind
    )

    red_districts = [d.district_name for d in risk_assessment.high_risk_districts if d.risk_level == "RED"]
    actions = action_engine.get_or_create_actions_for_cyclone(
        db=db,
        cyclone_id=cyclone_id,
        threat_level=risk_assessment.threat_level,
        red_districts=red_districts
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
    ai_briefing = data_bridge.get_ai_situation_briefing(
        cyclone_id=cyclone_id,
        exposure_summary=exposure_summary
    )

    return report_engine.generate_json_report(
        cyclone_id=cyclone_id,
        storm_data=storm,
        risk_assessment=risk_assessment,
        ai_briefing=ai_briefing,
        actions=actions
    )


@router.get("/situation-report/{cyclone_id}")
async def get_situation_report(
    cyclone_id: str,
    format: str = Query("pdf", description="Output format: 'pdf' or 'json'"),
    db: Session = Depends(get_db)
):
    """
    Unified endpoint to retrieve either PDF or JSON situation reports.
    """
    if format.lower() == "json":
        return await get_situation_report_json(cyclone_id=cyclone_id, db=db)
    return await get_situation_report_pdf(cyclone_id=cyclone_id, db=db)
