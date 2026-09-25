import pytest
import datetime
from geospatial_ai.gemini.ai_advisor import GeminiDisasterAdvisor
from geospatial_ai.schemas import CycloneData, GeospatialEvidence, Point
from geospatial_ai.gee.gee_pipeline import GEEPipeline

def test_gemini_fallback_mode_no_api_key():
    advisor = GeminiDisasterAdvisor(api_key="")
    now = datetime.datetime.now(datetime.timezone.utc)
    mock_storm = CycloneData(
        cyclone_id="CYC-TEST",
        name="Test Cyclone",
        source="synthetic_fixture",
        category=3,
        max_sustained_wind_kmh=150.0,
        current_position=Point(lat=10.0, lon=80.0, recorded_at=now)
    )
    mock_evidence = GEEPipeline().generate_evidence([80.0, 10.0, 81.0, 11.0], "2026-09-22")

    briefing = advisor.generate_situation_briefing(mock_storm, {"population": 1000}, mock_evidence)
    
    assert briefing.mode == "unavailable"
    assert briefing.threat_level == "UNKNOWN"
    assert len(briefing.critical_actions) == 0
    assert len(briefing.high_risk_districts) == 0
    assert "unavailable" in briefing.executive_summary.lower()
