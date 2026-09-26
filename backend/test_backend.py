"""
Backend Comprehensive Verification & Test Suite (Day 1 + Day 2 + Day 3 Readiness)
Owner: Krishna (Backend & Risk Engine Architect)
"""

import sys
import os

# Add backend and project root to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Remove old test sqlite db if exists for clean state test
test_db_path = os.path.join(backend_dir, "cyclone_risk.db")

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db, SessionLocal
from app.services.geometry_engine import geometry_engine
from app.services.risk_engine import risk_engine
from app.services.data_bridge import data_bridge
from app.db import models


def test_backend_suite():
    print("================================================================")
    print("🌪️  RUNNING FULL BACKEND DAY 2 VERIFICATION & TEST SUITE")
    print("================================================================")

    # 1. Database Initialization
    print("\n--- 1. Testing Database Initialization & Seeding ---")
    init_db()
    db = SessionLocal()
    district_count = db.query(models.DistrictDB).count()
    action_count = db.query(models.ActionItemDB).count()
    cyclone_count = db.query(models.CycloneEventDB).count()
    db.close()
    assert district_count >= 4, f"Expected at least 4 districts, got {district_count}"
    assert action_count >= 5, f"Expected at least 5 actions, got {action_count}"
    assert cyclone_count >= 1, f"Expected at least 1 cyclone, got {cyclone_count}"
    print(f" Database initialized: {district_count} districts, {action_count} actions, {cyclone_count} cyclone events.")

    client = TestClient(app)

    # 2. Root & Health Endpoints
    print("\n--- 2. Testing Root & Health Endpoints ---")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Root failed: {res_root.text}"
    assert res_root.json()["status"] == "online"
    print(f" Root endpoint OK: {res_root.json()}")

    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Health failed: {res_health.text}"
    assert res_health.json()["status"] == "healthy"
    print(f" Health check OK: {res_health.json()}")

    # 3. Cyclones & Tracking Endpoints
    print("\n--- 3. Testing Cyclones & Tracking Endpoints ---")
    res_active = client.get("/api/v1/cyclones/active")
    assert res_active.status_code == 200, f"Active cyclone failed: {res_active.text}"
    cyclone_data = res_active.json()
    assert cyclone_data["cyclone_id"] == "CYC-2026-01"
    assert cyclone_data["category"] == 3
    assert len(cyclone_data["forecast_track"]) >= 4
    assert len(cyclone_data["past_track"]) >= 4
    assert "current_position" in cyclone_data
    print(f" Active Cyclone: '{cyclone_data['name']}' (Cat {cyclone_data['category']}, {cyclone_data['max_sustained_wind_kmh']} km/h)")
    print(f"   Current Pos: ({cyclone_data['current_position']['lat']}, {cyclone_data['current_position']['lon']})")
    print(f"   Forecast points: {len(cyclone_data['forecast_track'])}, Past points: {len(cyclone_data['past_track'])}")

    res_all = client.get("/api/v1/cyclones/all")
    assert res_all.status_code == 200
    print(f" All Cyclones count: {len(res_all.json())}")

    # 4. Multi-Hazard Composite Risk Engine Endpoints
    print("\n--- 4. Testing Multi-Hazard Composite Risk & Exposure Endpoints ---")
    res_risk = client.get("/api/v1/risk/exposure/CYC-2026-01")
    assert res_risk.status_code == 200, f"Risk exposure failed: {res_risk.text}"
    risk_data = res_risk.json()
    assert risk_data["threat_level"] in ["RED", "ORANGE", "YELLOW", "GREEN"]
    assert len(risk_data["high_risk_districts"]) >= 4
    assert risk_data["total_population_at_risk"] > 0

    top_dist = risk_data["high_risk_districts"][0]
    print(f" Overall Threat Level: {risk_data['threat_level']}")
    print(f" Total Population at Risk: {risk_data['total_population_at_risk']:,}")
    print(f" Top Impact District: {top_dist['district_name']} (Score: {top_dist['risk_score']}/100, Tier: {top_dist['risk_level']})")
    print(f"   Flooded Area: {top_dist['flooded_area_sq_km']} sq km | Vulnerable Hospitals: {top_dist['vulnerable_hospitals']}")

    # Verify score bounds
    for d in risk_data["high_risk_districts"]:
        assert 0.0 <= d["risk_score"] <= 100.0, f"Score out of range: {d['risk_score']}"
        assert d["risk_level"] in ["RED", "ORANGE", "YELLOW", "GREEN"]

    res_districts = client.get("/api/v1/risk/districts/CYC-2026-01")
    assert res_districts.status_code == 200
    assert len(res_districts.json()) == len(risk_data["high_risk_districts"])
    print(f" District breakdown endpoint returned {len(res_districts.json())} districts.")

    # 5. Actions & SOP Triage Endpoints
    print("\n--- 5. Testing Actions SOP & Triage Engine Endpoints ---")
    res_actions = client.get("/api/v1/actions/recommendations/CYC-2026-01")
    assert res_actions.status_code == 200, f"Actions failed: {res_actions.text}"
    actions_data = res_actions.json()
    assert len(actions_data) >= 5
    print(f" Action recommendations generated: {len(actions_data)} items")
    for act in actions_data[:3]:
        print(f"   [{act['priority']}] ({act['phase']} - {act['sector']}) {act['instruction'][:65]}... -> Status: {act['status']}")

    # Test status update endpoint
    res_update = client.post("/api/v1/actions/update-status", json={
        "action_id": "ACT-001",
        "status": "COMPLETED"
    })
    assert res_update.status_code == 200, f"Update status failed: {res_update.text}"
    assert res_update.json()["updated_to"] == "COMPLETED"

    # Verify status in subsequent fetch
    res_actions_after = client.get("/api/v1/actions/recommendations/CYC-2026-01")
    act_001 = next(a for a in res_actions_after.json() if a["id"] == "ACT-001")
    assert act_001["status"] == "COMPLETED"
    print(f" Action state persistence verified: ACT-001 is now '{act_001['status']}'")

    # 6. Geospatial Layers, Cone of Uncertainty & Wind Buffers Endpoints
    print("\n--- 6. Testing Geospatial Layers, Cone & Wind Buffers Endpoints ---")
    res_layers = client.get("/api/v1/geospatial/layers")
    assert res_layers.status_code == 200, f"Geospatial layers failed: {res_layers.text}"
    layers_data = res_layers.json()
    assert "sar_flood" in layers_data["layers"]
    assert "gpm_rainfall" in layers_data["layers"]
    assert layers_data["layers"]["sar_flood"]["tile_url"] is not None
    assert layers_data["layers"]["gpm_rainfall"]["tile_url"] is not None
    print(f" GEE Tile Layers: SAR Flood ({layers_data['layers']['sar_flood']['status']}), GPM Rain ({layers_data['layers']['gpm_rainfall']['status']})")
    print(f"   SAR URL: {layers_data['layers']['sar_flood']['tile_url'][:60]}...")

    # Forecast Cone GeoJSON
    res_cone = client.get("/api/v1/geospatial/cone/CYC-2026-01")
    assert res_cone.status_code == 200, f"Forecast cone failed: {res_cone.text}"
    cone_data = res_cone.json()
    assert cone_data["type"] == "FeatureCollection"
    assert len(cone_data["features"]) > 0
    cone_geom = cone_data["features"][0]["geometry"]
    assert cone_geom["type"] == "Polygon"
    cone_coords = cone_geom["coordinates"][0]
    assert len(cone_coords) >= 10, f"Expected smooth cone polygon, got {len(cone_coords)} points"
    assert cone_coords[0] == cone_coords[-1], "Cone polygon must be closed"
    print(f" Dynamic Forecast Cone GeoJSON verified: {len(cone_coords)} vertices forming closed polygon.")

    # Wind Buffers GeoJSON (34kt, 50kt, 64kt)
    res_buffers = client.get("/api/v1/geospatial/wind-buffers/CYC-2026-01")
    assert res_buffers.status_code == 200, f"Wind buffers failed: {res_buffers.text}"
    buf_data = res_buffers.json()
    assert buf_data["type"] == "FeatureCollection"
    assert len(buf_data["features"]) == 3
    radii = [f["properties"]["radius_km"] for f in buf_data["features"]]
    print(f" Multi-tier Wind Buffers verified:")
    for feat in buf_data["features"]:
        props = feat["properties"]
        coords = feat["geometry"]["coordinates"][0]
        assert coords[0] == coords[-1], "Buffer circle polygon must be closed"
        print(f"   • {props['label']} ({props['wind_speed_kt']} kt / {props['wind_speed_kmh']} km/h) -> Radius: {props['radius_km']} km, Color: {props['color']}")

    # 7. Gemini AI Disaster Situation Briefing Endpoint
    print("\n--- 7. Testing Gemini AI Disaster Situation Briefing Endpoint ---")
    res_ai = client.get("/api/v1/ai/briefing/CYC-2026-01")
    assert res_ai.status_code == 200, f"AI briefing failed: {res_ai.text}"
    ai_data = res_ai.json()
    assert ai_data["cyclone_id"] == "CYC-2026-01"
    assert len(ai_data["executive_summary"]) > 20
    assert ai_data["threat_level"] in ["RED", "ORANGE", "YELLOW", "GREEN"]
    assert len(ai_data["critical_actions"]) > 0
    print(f" Gemini AI Briefing (Mode: {ai_data['mode']}):")
    print(f"   Summary: {ai_data['executive_summary'][:85]}...")
    print(f"   Threat Level: {ai_data['threat_level']} | High Risk Districts: {ai_data['high_risk_districts']}")
    print(f"   Critical Action Recommendations: {len(ai_data['critical_actions'])} items")

    # 8. Spatial Math & Geometry Engine Unit Tests
    print("\n--- 8. Testing Spatial Math & Geometry Engine Unit Functions ---")
    dist_nellore_chennai = geometry_engine.haversine_distance_km(14.4426, 79.9865, 13.0827, 80.2707)
    assert 150.0 < dist_nellore_chennai < 190.0, f"Haversine calculation unexpected: {dist_nellore_chennai}"
    print(f" Haversine Distance (Nellore to Chennai): {dist_nellore_chennai:.2f} km")

    circle = geometry_engine.create_circle_polygon(14.5, 82.1, 50.0, num_points=36)
    assert len(circle) == 37
    assert circle[0] == circle[-1]
    print(f" Circular Buffer Generator: 36 vertices + closing loop verified.")

    # 9. WebSocket Alerts Live Broadcast Channel
    print("\n--- 9. Testing WebSocket Alerts Live Broadcast Channel & Broadcaster ---")
    with client.websocket_connect("/api/v1/ws/alerts") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "SYSTEM_INFO"
        print(f" WebSocket Handshake Successful: {msg['message']}")
        ws.send_text("ping")
        resp = ws.receive_text()
        assert resp == "pong"
        print(" WebSocket Ping-Pong Heartbeat OK.")

        # Test POST /api/v1/ws/broadcast-alert pushing message to live client
        res_broadcast = client.post("/api/v1/ws/broadcast-alert", json={
            "type": "EMERGENCY_BROADCAST",
            "severity": "CRITICAL",
            "headline": "Storm Landfall Warning: Eye approaching Nellore within 18 hours.",
            "cyclone_id": "CYC-2026-01"
        })
        assert res_broadcast.status_code == 200
        broadcast_received = ws.receive_json()
        assert broadcast_received["type"] == "EMERGENCY_BROADCAST"
        assert broadcast_received["severity"] == "CRITICAL"
        print(f" WebSocket Alert Broadcast verified: Client received live alert '{broadcast_received['headline']}'")

    # 10. Official PDF & JSON Situation Report (SITREP) Generation (Day 3 Feature)
    print("\n--- 10. Testing Official Situation Report (SITREP) Endpoints (Day 3) ---")
    res_pdf = client.get("/api/v1/reports/situation-report/pdf/CYC-2026-01")
    assert res_pdf.status_code == 200, f"PDF report generation failed: {res_pdf.text}"
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF-"), "Response is not a valid PDF binary"
    assert len(res_pdf.content) > 3000, f"PDF content unexpectedly small: {len(res_pdf.content)} bytes"
    print(f" Official PDF Situation Report Generated Successfully: {len(res_pdf.content):,} bytes (Valid PDF binary)")

    # JSON Situation Report
    res_json_report = client.get("/api/v1/reports/situation-report/json/CYC-2026-01")
    assert res_json_report.status_code == 200, f"JSON report failed: {res_json_report.text}"
    report_data = res_json_report.json()
    assert report_data["cyclone_id"] == "CYC-2026-01"
    assert "storm_telemetry" in report_data
    assert "risk_assessment" in report_data
    assert "operational_actions" in report_data
    assert len(report_data["operational_actions"]) >= 5
    print(f" Structured JSON Situation Report Verified: Report ID {report_data['report_id']}")

    # Unified report endpoint
    res_unified_pdf = client.get("/api/v1/reports/situation-report/CYC-2026-01?format=pdf")
    assert res_unified_pdf.status_code == 200 and res_unified_pdf.content.startswith(b"%PDF-")
    res_unified_json = client.get("/api/v1/reports/situation-report/CYC-2026-01?format=json")
    assert res_unified_json.status_code == 200 and "report_id" in res_unified_json.json()
    print(" Unified Situation Report endpoint (?format=pdf/json) verified.")

    # Backward compatibility endpoint
    res_compat = client.get("/api/v1/risk/report/CYC-2026-01")
    assert res_compat.status_code == 200 and "report_id" in res_compat.json()
    print(" Backward compatibility endpoint /api/v1/risk/report/CYC-2026-01 verified.")

    # 11. Live Indian Ocean Marine Weather Endpoint
    res_marine = client.get("/api/v1/cyclones/marine/weather?lat=12.0&lon=86.0")
    assert res_marine.status_code == 200, f"Marine weather failed: {res_marine.text}"
    marine_data = res_marine.json()
    assert "wind_speed_kmh" in marine_data
    assert "wind_direction_cardinal" in marine_data
    assert "surface_pressure_hpa" in marine_data
    print(f" Live Indian Ocean Marine Telemetry OK: {marine_data['wind_speed_kmh']} km/h ({marine_data['wind_direction_cardinal']} {marine_data['wind_direction_deg']}°), Pressure: {marine_data['surface_pressure_hpa']} hPa")


    print("\n================================================================")
    print(" 🎉 ALL 10 COMPREHENSIVE TEST SUITES PASSED! DAY 3 COMPLETE.")
    print("================================================================")


if __name__ == "__main__":
    test_backend_suite()

