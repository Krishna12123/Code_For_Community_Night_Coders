"""
Geospatial AI Domain - Cyclone & Weather Data Ingestion Module
Owner: Vikash
"""

import datetime
from typing import Dict, Any, Optional
import requests
from geospatial_ai.schemas import CycloneData, Point, WeatherData

class CycloneTracker:
    """
    Ingests live and historical cyclone coordinates, wind speeds,
    central pressure, and marine weather forecasts.
    """

    def __init__(self):
        self.open_meteo_url = "https://api.open-meteo.com/v1/forecast"

    def get_active_cyclone(self, cyclone_id: str = "CYC-2026-01") -> CycloneData:
        """
        Fetches or simulates the latest active cyclone tracking data
        including historical path and forecasted cone points.
        Returns a validated CycloneData Pydantic model.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Explicitly return a synthetic fixture for Day 1
        active_storm = CycloneData(
            cyclone_id=cyclone_id,
            name="Cyclone Vardah-II",
            source="synthetic_fixture",
            category=3,
            max_sustained_wind_kmh=165.0,
            central_pressure_mb=960.0,
            current_position=Point(
                lat=14.5,
                lon=82.1,
                recorded_at=now,
                wind_kmh=165.0
            ),
            past_track=[
                Point(lat=12.8, lon=85.2, recorded_at=now - datetime.timedelta(hours=18), wind_kmh=110.0),
                Point(lat=13.4, lon=84.1, recorded_at=now - datetime.timedelta(hours=12), wind_kmh=135.0),
                Point(lat=14.0, lon=83.0, recorded_at=now - datetime.timedelta(hours=6), wind_kmh=150.0),
                Point(lat=14.5, lon=82.1, recorded_at=now, wind_kmh=165.0),
            ],
            forecast_track=[
                Point(lat=15.0, lon=81.3, recorded_at=now + datetime.timedelta(hours=6), wind_kmh=175.0, uncertainty_radius_km=35.0),
                Point(lat=15.6, lon=80.5, recorded_at=now + datetime.timedelta(hours=12), wind_kmh=180.0, uncertainty_radius_km=50.0),
                Point(lat=16.1, lon=79.8, recorded_at=now + datetime.timedelta(hours=18), wind_kmh=150.0, uncertainty_radius_km=70.0),
                Point(lat=16.7, lon=79.1, recorded_at=now + datetime.timedelta(hours=24), wind_kmh=95.0, uncertainty_radius_km=90.0),
            ]
        )
        return active_storm

    def fetch_live_marine_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """
        Fetches live wind and atmospheric conditions via Open-Meteo API.
        Returns validated WeatherData or None if it fails.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["wind_speed_10m", "wind_direction_10m", "surface_pressure", "precipitation"],
            "hourly": ["wind_speed_10m", "precipitation"]
        }
        try:
            response = requests.get(self.open_meteo_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                return WeatherData(
                    source="live",
                    wind_speed_kmh=float(current.get("wind_speed_10m", 0.0)),
                    wind_direction_deg=float(current.get("wind_direction_10m", 0.0)),
                    surface_pressure_hpa=float(current.get("surface_pressure", 1013.25)),
                    precipitation_mm=float(current.get("precipitation", 0.0))
                )
        except requests.exceptions.RequestException as e:
            print(f"[Warning] Failed to fetch live weather: {e}")
        except Exception as e:
            print(f"[Warning] Unexpected error parsing weather: {e}")
            
        return None

if __name__ == "__main__":
    tracker = CycloneTracker()
    cyclone = tracker.get_active_cyclone()
    print(f"Loaded Cyclone: {cyclone.name} | Category: {cyclone.category} | Wind: {cyclone.max_sustained_wind_kmh} km/h")
