import os
import json
from pathlib import Path
from geospatial_ai.data_ingestion.cyclone_tracker import CycloneTracker
from geospatial_ai.gee.gee_pipeline import GEEPipeline
from geospatial_ai.gemini.ai_advisor import GeminiDisasterAdvisor

def run():
    print("--- Cyclone Risk Assessment - Geospatial AI Pipeline Demo ---")
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 1. Cyclone Data
    print("\n[1] Ingesting Cyclone Tracker Data...")
    tracker = CycloneTracker()
    cyclone_data = tracker.get_active_cyclone()
    weather_data = tracker.fetch_live_marine_weather(
        cyclone_data.current_position.lat, 
        cyclone_data.current_position.lon
    )
    
    with open(output_dir / "cyclone_data.json", "w") as f:
        # Pydantic dump
        f.write(cyclone_data.model_dump_json(indent=2))
    print(f"    -> Saved cyclone_data.json (Source: {cyclone_data.source})")
    
    if weather_data:
        print(f"    -> Weather fetched: {weather_data.wind_speed_kmh} km/h (Source: {weather_data.source})")

    # 2. GEE Evidence
    print("\n[2] Initializing GEE Pipeline...")
    gee = GEEPipeline()
    gee.initialize_gee()
    
    print("    -> Generating Geospatial Evidence...")
    # Using a bounding box around current position for demo
    lat, lon = cyclone_data.current_position.lat, cyclone_data.current_position.lon
    bbox = [lon - 2, lat - 2, lon + 2, lat + 2]
    evidence = gee.generate_evidence(bbox, cyclone_data.current_position.recorded_at.isoformat())
    
    with open(output_dir / "geospatial_evidence.json", "w") as f:
        f.write(evidence.model_dump_json(indent=2))
    print("    -> Saved geospatial_evidence.json")
    
    # 3. Gemini Advisory
    print("\n[3] Generating Gemini Advisory Briefing...")
    advisor = GeminiDisasterAdvisor()
    
    # Mock exposure data for Day 1
    exposure_mock = {
        "total_population_at_risk": 1850000,
        "critical_infrastructure_count": 12
    }
    
    advisory = advisor.generate_situation_briefing(cyclone_data, exposure_mock, evidence)
    
    with open(output_dir / "advisory.json", "w") as f:
        f.write(advisory.model_dump_json(indent=2))
    print(f"    -> Saved advisory.json (Mode: {advisory.mode})")
    print("\n--- Pipeline Complete! Output files in geospatial_ai/output/ ---")


if __name__ == "__main__":
    run()
