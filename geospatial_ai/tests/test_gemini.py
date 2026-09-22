import pytest
import datetime
from geospatial_ai.gemini.ai_advisor import GeminiDisasterAdvisor
from geospatial_ai.schemas import CycloneData, GeospatialEvidence, Point, AdvisoryBriefing

@pytest.fixture
def mock_storm():
    now = datetime.datetime.now(datetime.timezone.utc)
    return CycloneData(
        cyclone_id="CYC-TEST",
        name="Test Cyclone",
        source="synthetic_fixture",
        category=3,
        max_sustained_wind_kmh=150.0,
        current_position=Point(lat=10.0, lon=80.0, recorded_at=now)
    )

@pytest.fixture
def mock_evidence():
    from geospatial_ai.gee.gee_pipeline import GEEPipeline
    pipeline = GEEPipeline(project_id=None)
    pipeline.initialize_gee()
    return pipeline.generate_evidence([80.0, 10.0, 81.0, 11.0], "today")

def test_gemini_fallback(mock_storm, mock_evidence):
    # Pass no API key so it uses fallback
    advisor = GeminiDisasterAdvisor(api_key=None)
    briefing = advisor.generate_situation_briefing(
        mock_storm,
        {"total_population_at_risk": 1850000},
        mock_evidence
    )
    
    assert isinstance(briefing, AdvisoryBriefing)
    assert briefing.mode == "demo_fixture"
    assert "simulated demo scenario" in briefing.executive_summary.lower()
    assert briefing.threat_level == "RED"
    assert len(briefing.critical_actions) > 0

def test_gemini_api_success(mocker, mock_storm, mock_evidence):
    advisor = GeminiDisasterAdvisor(api_key="fake-key")
    
    # Mock genai client
    mock_client = mocker.Mock()
    mock_response = mocker.Mock()
    mock_response.text = '{"executive_summary": "Test Summary", "threat_level": "ORANGE", "high_risk_districts": ["D1"], "critical_actions": [{"priority": "HIGH", "phase": "PRE_LANDFALL", "sector": "Evac", "instruction": "Test"}], "mode": "live"}'
    mock_client.models.generate_content.return_value = mock_response
    
    mocker.patch('geospatial_ai.gemini.ai_advisor.genai.Client', return_value=mock_client)
    
    briefing = advisor.generate_situation_briefing(
        mock_storm,
        {"total_population_at_risk": 1850000},
        mock_evidence
    )
    
    assert isinstance(briefing, AdvisoryBriefing)
    assert briefing.threat_level == "ORANGE"
    assert briefing.executive_summary == "Test Summary"

def test_gemini_api_malformed_json_fallback(mocker, mock_storm, mock_evidence):
    advisor = GeminiDisasterAdvisor(api_key="fake-key")
    
    # Mock genai client returning invalid JSON
    mock_client = mocker.Mock()
    mock_response = mocker.Mock()
    mock_response.text = '{"bad_json": true'
    mock_client.models.generate_content.return_value = mock_response
    
    mocker.patch('geospatial_ai.gemini.ai_advisor.genai.Client', return_value=mock_client)
    
    briefing = advisor.generate_situation_briefing(
        mock_storm,
        {"total_population_at_risk": 1850000},
        mock_evidence
    )
    
    # Must fallback to demo_fixture
    assert isinstance(briefing, AdvisoryBriefing)
    assert briefing.mode == "demo_fixture"
