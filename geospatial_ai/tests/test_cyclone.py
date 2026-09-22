import pytest
import requests
from datetime import datetime
from geospatial_ai.data_ingestion.cyclone_tracker import CycloneTracker
from geospatial_ai.schemas import CycloneData, WeatherData

def test_get_active_cyclone():
    tracker = CycloneTracker()
    cyclone = tracker.get_active_cyclone("CYC-TEST-01")
    
    assert isinstance(cyclone, CycloneData)
    assert cyclone.cyclone_id == "CYC-TEST-01"
    assert cyclone.source == "synthetic_fixture"
    assert cyclone.category == 3
    assert len(cyclone.past_track) > 0
    assert len(cyclone.forecast_track) > 0

    # Ensure timezone aware
    assert cyclone.current_position.recorded_at.tzinfo is not None

def test_fetch_live_marine_weather_success(mocker):
    tracker = CycloneTracker()
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {
            "wind_speed_10m": 120.5,
            "wind_direction_10m": 90,
            "surface_pressure": 980.0,
            "precipitation": 15.0
        }
    }
    
    mocker.patch('requests.get', return_value=mock_response)
    
    weather = tracker.fetch_live_marine_weather(15.0, 80.0)
    
    assert isinstance(weather, WeatherData)
    assert weather.source == "live"
    assert weather.wind_speed_kmh == 120.5
    assert weather.wind_direction_deg == 90.0
    assert weather.surface_pressure_hpa == 980.0
    assert weather.precipitation_mm == 15.0

def test_fetch_live_marine_weather_failure(mocker):
    tracker = CycloneTracker()
    
    # Simulate network failure
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError("Network down"))
    
    weather = tracker.fetch_live_marine_weather(15.0, 80.0)
    
    # Must not invent data on failure
    assert weather is None

def test_fetch_live_marine_weather_malformed(mocker):
    tracker = CycloneTracker()
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"current": {"wrong_field": 123}}
    
    mocker.patch('requests.get', return_value=mock_response)
    
    weather = tracker.fetch_live_marine_weather(15.0, 80.0)
    
    assert isinstance(weather, WeatherData)
    assert weather.wind_speed_kmh == 0.0 # Defaults appropriately
