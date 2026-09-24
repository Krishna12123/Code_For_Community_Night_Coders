import pytest
import datetime
from unittest.mock import MagicMock
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
    assert evidence.flood.flooded_area_sq_km is None
    
    # Check rainfall
    assert evidence.rainfall.dataset == "NASA/GPM_L3/IMERG_V07"
    assert evidence.rainfall.status == "unavailable"
    assert evidence.rainfall.reason == "offline"
    assert evidence.rainfall.tile_url is None
    assert evidence.rainfall.accumulation_mm is None

def test_gee_pipeline_empty_s1_collection(mocker):
    # Mock 'ee' module
    mock_ee = MagicMock()
    mocker.patch.dict('sys.modules', {'ee': mock_ee})
    
    pipeline = GEEPipeline(project_id="test-project")
    pipeline.initialized = True
    pipeline.offline_mode = False
    
    # Mock collection size to return 0 for S1
    mock_collection = MagicMock()
    mock_collection.filterBounds.return_value = mock_collection
    mock_collection.filter.return_value = mock_collection
    mock_collection.select.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_collection
    
    size_mock = MagicMock()
    size_mock.getInfo.return_value = 0
    mock_collection.size.return_value = size_mock
    
    mock_ee.ImageCollection.return_value = mock_collection
    
    layer = pipeline.get_sar_flood_layer([80, 10, 81, 11], datetime.datetime.utcnow())
    assert layer.status == "unavailable"
    assert "No Sentinel-1 imagery available" in layer.reason
    assert layer.flooded_area_sq_km is None

def test_gee_pipeline_empty_gpm_collection(mocker):
    mock_ee = MagicMock()
    mocker.patch.dict('sys.modules', {'ee': mock_ee})
    
    pipeline = GEEPipeline(project_id="test-project")
    pipeline.initialized = True
    pipeline.offline_mode = False
    
    mock_collection = MagicMock()
    mock_collection.filterBounds.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_collection
    mock_collection.select.return_value = mock_collection
    
    size_mock = MagicMock()
    size_mock.getInfo.return_value = 0
    mock_collection.size.return_value = size_mock
    
    mock_ee.ImageCollection.return_value = mock_collection
    
    layer = pipeline.get_gpm_rainfall_layer([80, 10, 81, 11], datetime.datetime.utcnow())
    assert layer.status == "unavailable"
    assert "No GPM IMERG imagery available" in layer.reason
    assert layer.accumulation_mm is None

def test_gee_pipeline_gpm_aggregation_logic(mocker):
        # We want to verify that .multiply(0.5) is called on the image
        mock_ee = MagicMock()
        mocker.patch.dict('sys.modules', {'ee': mock_ee})
    
        pipeline = GEEPipeline(project_id="test-project")
        pipeline.initialized = True
        pipeline.offline_mode = False
    
        mock_collection = MagicMock()
        mock_collection.filterBounds.return_value = mock_collection
        mock_collection.filterDate.return_value = mock_collection
        mock_collection.select.return_value = mock_collection
        
        size_mock = MagicMock()
        size_mock.getInfo.return_value = 5 # Collection is not empty
        mock_collection.size.return_value = size_mock
    
        # Track what happens in map()
        def fake_map(func):
            # Pass a mock image to the map function to test the conversion logic
            mock_img = MagicMock()
            mock_img.multiply.return_value = mock_img
            mock_img.copyProperties.return_value = mock_img
            func(mock_img)
            # Verify 0.5 was passed to multiply
            mock_img.multiply.assert_called_with(0.5)
            return mock_collection
    
        mock_collection.map = fake_map
        mock_collection.sum.return_value = mock_collection
        mock_collection.clip.return_value = mock_collection
    
        # Mock reduceRegion
        stats_mock = MagicMock()
        stats_mock.get.return_value.getInfo.return_value = 150.0
        mock_collection.reduceRegion.return_value = stats_mock
    
        # Mock getMapId
        from collections import namedtuple
        Fetcher = namedtuple('Fetcher', ['url_format'])
        mock_collection.getMapId.return_value = {"tile_fetcher": Fetcher(url_format="https://earthengine.googleapis.com/.../tile")}
    
        mock_ee.ImageCollection.return_value = mock_collection
    
        layer = pipeline.get_gpm_rainfall_layer([80, 10, 81, 11], datetime.datetime.utcnow())
    
        assert layer.status == "available", layer.reason
        assert layer.accumulation_mm == 150.0
        assert layer.tile_url is not None
    
def test_gee_pipeline_s1_area_conversion(mocker):
        mock_ee = MagicMock()
        mocker.patch.dict('sys.modules', {'ee': mock_ee})
    
        pipeline = GEEPipeline(project_id="test-project")
        pipeline.initialized = True
        pipeline.offline_mode = False
    
        mock_collection = MagicMock()
        mock_collection.filterBounds.return_value = mock_collection
        mock_collection.filter.return_value = mock_collection
        mock_collection.select.return_value = mock_collection
        mock_collection.filterDate.return_value = mock_collection
        
        size_mock = MagicMock()
        size_mock.getInfo.return_value = 1
        mock_collection.size.return_value = size_mock
        mock_ee.ImageCollection.return_value = mock_collection
    
        # Area in m2 = 5,000,000 m2 (which should be 5.0 km2)
        stats_mock = MagicMock()
        stats_mock.get.return_value.getInfo.return_value = 5000000.0
    
        # Deep mock to bypass the method chain and inject the stats_mock at reduceRegion
        mock_img = MagicMock()
        mock_img.reduceRegion.return_value = stats_mock
        mock_img.multiply.return_value = mock_img
    
        # This is a bit brittle, but we patch reduceRegion on whatever flood_mask.multiply returns
        mock_mask = MagicMock()
        mock_mask.multiply.return_value = mock_img
        mock_mask.And.return_value = mock_mask
        mock_mask.lt.return_value = mock_mask
    
        # Just force the difference to return our mock mask
        mock_pre = MagicMock()
        mock_post = MagicMock()
        mock_post.subtract.return_value = mock_mask
    
        mock_collection.mosaic.return_value.focal_median.side_effect = [mock_pre, mock_post]
    
        # Mock JRC and DEM
        mock_ee.Image.return_value.select.return_value.unmask.return_value.lt.return_value = mock_mask
        mock_ee.Terrain.slope.return_value.lt.return_value = mock_mask
    
        from collections import namedtuple
        Fetcher = namedtuple('Fetcher', ['url_format'])
        mock_mask.updateMask.return_value.getMapId.return_value = {"tile_fetcher": Fetcher(url_format="https://earthengine.googleapis.com/.../tile")}
    
        layer = pipeline.get_sar_flood_layer([80, 10, 81, 11], datetime.datetime.utcnow())
    
        # Validate m2 to km2 conversion
        assert layer.status == "available", layer.reason
        assert layer.flooded_area_sq_km == 5.0
