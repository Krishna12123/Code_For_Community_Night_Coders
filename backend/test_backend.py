"""
Backend Verification & Test Suite
Owner: Krishna
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db

def test_backend_suite():
    print("--- 1. Testing Database Initialization ---")
    init_db()
    print(" Database initialized successfully.")

    client = TestClient(app)

    print("\n--- 2. Testing Root & Health Endpoints ---")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Root failed: {res_root.text}"
    print(f" Root endpoint OK: {res_root.json()}")

    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Health failed: {res_health.text}"
    print(f" Health check OK: {res_health.json()}")

    print("\n--- 3. Testing Cyclones Endpoints ---")
    res_active = client.get("/api/v1/cyclones/active")
    assert res_active.status_code == 200, f"Active cyclone failed: {res_active.text}"
    cyclone_data = res_active.json()
    assert cyclone_data["cyclone_id"] == "CYC-2026-01"
    assert cyclone_data["category"] == 3
    assert len(cyclone_data["forecast_track"]) == 4
    print(f" Active Cyclone: {cyclone_data['name']} (Cat {cyclone_data['category']}, {cyclone_data['max_sustained_wind_kmh']} km/h)")

    res_all = client.get("/api/v1/cyclones/all")
    assert res_all.status_code == 200
    print(f" All Cyclones count: {len(res_all.json())}")

    print("\n--- 4. Testing Risk & Exposure Endpoints ---")
    res_risk = client.get("/api/v1/risk/exposure/CYC-2026-01")
    assert res_risk.status_code == 200, f"Risk exposure failed: {res_risk.text}"
    risk_data = res_risk.json()
    assert risk_data["threat_level"] == "RED"
    assert len(risk_data["high_risk_districts"]) >= 4
    print(f" Risk Assessment: Threat Level {risk_data['threat_level']}, Population at Risk: {risk_data['total_population_at_risk']}")

    res_districts = client.get("/api/v1/risk/districts/CYC-2026-01")
    assert res_districts.status_code == 200
    print(f" District breakdown count: {len(res_districts.json())}")

    print("\n--- 5. Testing Actions & SOP Endpoints ---")
    res_actions = client.get("/api/v1/actions/recommendations/CYC-2026-01")
    assert res_actions.status_code == 200, f"Actions failed: {res_actions.text}"
    actions_data = res_actions.json()
    assert len(actions_data) >= 5
    print(f" Action recommendations count: {len(actions_data)}")

    # Test status update
    res_update = client.post("/api/v1/actions/update-status", json={
        "action_id": "ACT-001",
        "status": "COMPLETED"
    })
    assert res_update.status_code == 200, f"Update status failed: {res_update.text}"
    print(f" Status Update Response: {res_update.json()}")

    # Verify updated status
    res_actions_after = client.get("/api/v1/actions/recommendations/CYC-2026-01")
    act_001 = next(a for a in res_actions_after.json() if a["id"] == "ACT-001")
    assert act_001["status"] == "COMPLETED"
    print(f" Action ACT-001 verified as COMPLETED in database.")

    print("\n--- 6. Testing Geospatial Endpoints ---")
    res_layers = client.get("/api/v1/geospatial/layers")
    assert res_layers.status_code == 200, f"Geospatial layers failed: {res_layers.text}"
    layers_data = res_layers.json()
    assert "sar_flood" in layers_data["layers"]
    assert "gpm_rainfall" in layers_data["layers"]
    print(f" Geospatial Layers: SAR flood ({layers_data['layers']['sar_flood']['status']}) & GPM rainfall ({layers_data['layers']['gpm_rainfall']['status']})")

    res_cone = client.get("/api/v1/geospatial/cone/CYC-2026-01")
    assert res_cone.status_code == 200, f"Forecast cone failed: {res_cone.text}"
    cone_data = res_cone.json()
    assert cone_data["type"] == "FeatureCollection"
    assert len(cone_data["features"]) > 0
    print(f" Forecast Cone GeoJSON Polygon verified.")

    print("\n--- 7. Testing WebSocket Alerts Endpoint ---")
    with client.websocket_connect("/api/v1/ws/alerts") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "SYSTEM_INFO"
        print(f" WebSocket Connected successfully: {msg['message']}")
        ws.send_text("ping")
        resp = ws.receive_text()
        assert resp == "pong"
        print(" WebSocket ping-pong OK.")

    print("\n ALL BACKEND TESTS PASSED SUCCESSFULLY! ")

if __name__ == "__main__":
    test_backend_suite()
