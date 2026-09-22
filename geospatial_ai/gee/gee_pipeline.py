"""
Geospatial AI Domain - Google Earth Engine (GEE) Processing Pipeline
Owner: Vikash
"""

import os
import datetime
from typing import Dict, Any, List
from geospatial_ai.schemas import GeospatialEvidence, LayerInfo

class GEEPipeline:
    """
    Handles Sentinel-1 SAR flood extent mapping, GPM rainfall accumulation,
    and structured geospatial evidence generation.
    """

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("GEE_PROJECT_ID")
        self.initialized = False
        self.offline_mode = False

    def initialize_gee(self):
        """
        Initializes the Earth Engine API.
        """
        if not self.project_id:
            print("[GEE] No GEE_PROJECT_ID provided. Running in offline/mock mode.")
            self.offline_mode = True
            return

        try:
            import ee
            ee.Initialize(project=self.project_id)
            self.initialized = True
            print("[GEE] Earth Engine initialized successfully.")
        except Exception as e:
            print(f"[GEE] Failed to initialize GEE. Running in offline/mock mode. ({e})")
            self.offline_mode = True
            self.initialized = False

    def get_sar_flood_layer(self, bbox: list, start_date: str, end_date: str) -> LayerInfo:
        """
        Sentinel-1 SAR mosaic and VV backscatter threshold heuristic (Day 1).
        Genuine before/after change detection will be implemented in Day 2.
        """
        if self.initialized and not self.offline_mode:
            try:
                import ee
                roi = ee.Geometry.BBox(*bbox)
                s1 = (
                    ee.ImageCollection("COPERNICUS/S1_GRD")
                    .filterBounds(roi)
                    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
                    .filter(ee.Filter.eq("instrumentMode", "IW"))
                    .select("VV")
                )
                flood_mask = s1.filterDate(start_date, end_date).mosaic().lt(-16)
                vis_params = {"palette": ["#0055ff", "#00ffff"]}
                map_id = flood_mask.updateMask(flood_mask).getMapId(vis_params)
                
                return LayerInfo(
                    dataset="COPERNICUS/S1_GRD",
                    status="available",
                    start_date=start_date,
                    end_date=end_date,
                    tile_url=map_id["tile_fetcher"].url_format
                )
            except Exception as e:
                return LayerInfo(
                    dataset="COPERNICUS/S1_GRD",
                    status="unavailable",
                    reason=f"GEE processing error: {e}"
                )
                
        # Mock/Offline response
        return LayerInfo(
            dataset="COPERNICUS/S1_GRD",
            status="unavailable",
            start_date=start_date,
            end_date=end_date,
            tile_url=None,
            reason="offline"
        )

    def get_gpm_rainfall_layer(self, bbox: list, start_date: str, end_date: str) -> LayerInfo:
        """
        Generates NASA GPM IMERG precipitation accumulation layer.
        (Accumulation metric calculation deferred to Day 2 using ee.Reducer).
        """
        if self.initialized and not self.offline_mode:
            try:
                import ee
                roi = ee.Geometry.BBox(*bbox)
                gpm = (
                    ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
                    .filterBounds(roi)
                    .filterDate(start_date, end_date)
                    .select("precipitation")
                )
                accum = gpm.sum().clip(roi)
                
                vis_params = {"min": 0, "max": 200, "palette": ['blue', 'purple', 'yellow', 'red']}
                map_id = accum.getMapId(vis_params)

                return LayerInfo(
                    dataset="NASA/GPM_L3/IMERG_V07",
                    status="available",
                    start_date=start_date,
                    end_date=end_date,
                    accumulation_mm=None,
                    tile_url=map_id["tile_fetcher"].url_format
                )
            except Exception as e:
                return LayerInfo(
                    dataset="NASA/GPM_L3/IMERG_V07",
                    status="unavailable",
                    reason=f"GEE processing error: {e}"
                )

        return LayerInfo(
            dataset="NASA/GPM_L3/IMERG_V07",
            status="unavailable",
            start_date=start_date,
            end_date=end_date,
            accumulation_mm=None,
            tile_url=None,
            reason="offline"
        )

    def generate_evidence(self, bbox: list, date_str: str) -> GeospatialEvidence:
        """
        Returns structured evidence.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        start_date = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")

        flood_layer = self.get_sar_flood_layer(bbox, start_date, end_date)
        rain_layer = self.get_gpm_rainfall_layer(bbox, start_date, end_date)

        return GeospatialEvidence(
            analysis_region={"bbox": bbox, "date": date_str},
            rainfall=rain_layer,
            flood=flood_layer,
            generated_at=now
        )


if __name__ == "__main__":
    pipeline = GEEPipeline()
    pipeline.initialize_gee()
    evidence = pipeline.generate_evidence([80.0, 13.0, 84.0, 17.0], "2026-09-22")
    print("Generated Evidence:", evidence.model_dump_json(indent=2))
