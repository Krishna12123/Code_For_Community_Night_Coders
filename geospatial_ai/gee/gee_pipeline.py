"""
Geospatial AI Domain - Google Earth Engine (GEE) Processing Pipeline
Owner: Vikash
"""

import os
import datetime
from typing import Dict, Any, List, Optional
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

    def get_sar_flood_layer(self, bbox: list, landfall_date: datetime.datetime) -> LayerInfo:
        """
        Sentinel-1 SAR change-based flood heuristic.
        Computes the log-ratio difference between pre-storm and post-storm backscatter.
        """
        pre_start = (landfall_date - datetime.timedelta(days=15)).strftime("%Y-%m-%d")
        pre_end = (landfall_date - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        post_start = landfall_date.strftime("%Y-%m-%d")
        post_end = (landfall_date + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

        if self.initialized and not self.offline_mode:
            try:
                import ee
                roi = ee.Geometry.BBox(*bbox)
                
                # Fetch collections
                s1 = (
                    ee.ImageCollection("COPERNICUS/S1_GRD")
                    .filterBounds(roi)
                    .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
                    .filter(ee.Filter.eq("instrumentMode", "IW"))
                    .select("VV")
                )
                
                pre_collection = s1.filterDate(pre_start, pre_end)
                post_collection = s1.filterDate(post_start, post_end)
                
                # Graceful handling of empty collections due to Sentinel-1 revisit limitations
                if pre_collection.size().getInfo() == 0 or post_collection.size().getInfo() == 0:
                    return LayerInfo(
                        dataset="COPERNICUS/S1_GRD",
                        status="unavailable",
                        start_date=post_start,
                        end_date=post_end,
                        tile_url=None,
                        reason="No Sentinel-1 imagery available in requested temporal windows."
                    )
                
                # Preprocessing: speckle reduction using focal median
                pre_img = pre_collection.mosaic().focal_median(3)
                post_img = post_collection.mosaic().focal_median(3)
                
                # Change heuristic: Log-ratio subtraction (since GRD is in dB)
                difference = post_img.subtract(pre_img)
                
                # Flood heuristic
                flood_heuristic = difference.lt(-3).And(post_img.lt(-16))
                
                # Masking: Permanent water (JRC) and terrain slopes (SRTM)
                jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").unmask(0)
                srtm = ee.Image("CGIAR/SRTM90_V4")
                slope = ee.Terrain.slope(srtm)
                
                # Remove permanent water (occurrence > 10%) and steep terrain (> 5 degrees)
                flood_mask = flood_heuristic.And(jrc.lt(10)).And(slope.lt(5))
                
                # Calculate flooded area
                # Multiply binary mask by pixel area in m2, then sum over AOI
                area_img = flood_mask.multiply(ee.Image.pixelArea())
                stats = area_img.reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=roi,
                    scale=500, # Moderate resolution to prevent computation timeouts
                    maxPixels=1e10
                )
                
                # Convert square meters to square kilometers
                area_m2 = stats.get("VV").getInfo()
                flooded_area_sq_km = area_m2 / 1e6 if area_m2 else 0.0
                
                vis_params = {"palette": ["#00ffff"]}
                # Update mask so only flooded pixels render
                map_id = flood_mask.updateMask(flood_mask).getMapId(vis_params)
                
                return LayerInfo(
                    dataset="COPERNICUS/S1_GRD",
                    status="available",
                    start_date=post_start,
                    end_date=post_end,
                    flooded_area_sq_km=flooded_area_sq_km,
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
            start_date=post_start,
            end_date=post_end,
            flooded_area_sq_km=None,
            tile_url=None,
            reason="offline"
        )

    def get_gpm_rainfall_layer(self, bbox: list, landfall_date: datetime.datetime) -> LayerInfo:
        """
        IMERG rainfall accumulation.
        Generates NASA GPM IMERG precipitation accumulation layer.
        """
        # Rainfall window: e.g. 2 days before to 2 days after
        start_date = (landfall_date - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = (landfall_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

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
                
                if gpm.size().getInfo() == 0:
                    return LayerInfo(
                        dataset="NASA/GPM_L3/IMERG_V07",
                        status="unavailable",
                        start_date=start_date,
                        end_date=end_date,
                        accumulation_mm=None,
                        tile_url=None,
                        reason="No GPM IMERG imagery available for temporal window."
                    )

                # The precipitation band is mm/hr. 
                # Since IMERG half-hourly product provides 30-min data, multiply by 0.5 to get mm.
                def convert_to_mm(img):
                    return img.multiply(0.5).copyProperties(img, img.propertyNames())

                accum = gpm.map(convert_to_mm).sum().clip(roi)
                
                # Spatial reduction: find the maximum accumulated rainfall at any pixel within the AOI
                stats = accum.reduceRegion(
                    reducer=ee.Reducer.max(),
                    geometry=roi,
                    scale=10000, # Native resolution is ~11km
                    maxPixels=1e9
                )
                
                max_accum_mm = stats.get("precipitation").getInfo()
                
                vis_params = {"min": 0, "max": 300, "palette": ['blue', 'purple', 'yellow', 'red']}
                map_id = accum.getMapId(vis_params)

                return LayerInfo(
                    dataset="NASA/GPM_L3/IMERG_V07",
                    status="available",
                    start_date=start_date,
                    end_date=end_date,
                    accumulation_mm=max_accum_mm,
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
        
        # Parse the cyclone analysis/landfall date
        try:
            # Handle ISO formats and generic YYYY-MM-DD
            if "T" in date_str:
                landfall_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                landfall_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            landfall_date = now

        flood_layer = self.get_sar_flood_layer(bbox, landfall_date)
        rain_layer = self.get_gpm_rainfall_layer(bbox, landfall_date)

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
