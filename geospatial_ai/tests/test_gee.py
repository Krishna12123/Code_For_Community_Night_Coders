import pytest
from geospatial_ai.gee.gee_pipeline import GEEPipeline
from geospatial_ai.schemas import GeospatialEvidence

def test_gee_pipeline_offline_initialization():
    pipeline = GEEPipeline(project_id=None) # Explicitly no project
    pipeline.initialize_gee()
    
    assert pipeline.initialized is False
    assert pipeline.offline_mode is True

def test_gee_pipeline_offline_evidence():
    pipeline = GEEPipeline(project_id=None)
    pipeline.initialize_gee()
    
    evidence = pipeline.generate_evidence([80.0, 13.0, 84.0, 17.0], "2026-09-22")
    
    assert isinstance(evidence, GeospatialEvidence)
    
    # Check flood
    assert evidence.flood.dataset == "COPERNICUS/S1_GRD"
    assert evidence.flood.status == "unavailable"
    assert evidence.flood.reason == "offline"
    assert evidence.flood.tile_url is None
    
    # Check rainfall
    assert evidence.rainfall.dataset == "NASA/GPM_L3/IMERG_V07"
    assert evidence.rainfall.status == "unavailable"
    assert evidence.rainfall.reason == "offline"
    assert evidence.rainfall.tile_url is None
    assert evidence.rainfall.accumulation_mm is None
