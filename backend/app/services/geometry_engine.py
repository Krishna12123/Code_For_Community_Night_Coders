"""
Geometry & Spatial Buffering Engine
Owner: Krishna (Backend & Risk Engine Architect)
"""

import math
from typing import List, Dict, Any, Tuple
from app.schemas.models import (
    ForecastConeResponse,
    ConeFeature,
    ConeGeometry,
    WindBufferResponse,
    WindBufferFeature
)

EARTH_RADIUS_KM = 6371.0


class GeometryEngine:
    """
    Computes spatial geometries:
    1. Cone of Uncertainty polygons from forecast track & uncertainty radii.
    2. 34kt, 50kt, 64kt wind swath buffer polygons.
    3. Haversine distance calculations for district exposure.
    """

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates great-circle distance between two points in kilometers.
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_KM * c

    @staticmethod
    def destination_point(lat: float, lon: float, distance_km: float, bearing_deg: float) -> Tuple[float, float]:
        """
        Calculates destination point given start point, distance, and bearing.
        Returns (lon, lat) formatted for GeoJSON coordinates.
        """
        delta = distance_km / EARTH_RADIUS_KM
        theta = math.radians(bearing_deg)
        phi1 = math.radians(lat)
        lambda1 = math.radians(lon)

        phi2 = math.asin(
            math.sin(phi1) * math.cos(delta)
            + math.cos(phi1) * math.sin(delta) * math.cos(theta)
        )
        lambda2 = lambda1 + math.atan2(
            math.sin(theta) * math.sin(delta) * math.cos(phi1),
            math.cos(delta) - math.sin(phi1) * math.sin(phi2)
        )

        return (math.degrees(lambda2), math.degrees(phi2))

    def create_circle_polygon(self, lat: float, lon: float, radius_km: float, num_points: int = 36) -> List[List[float]]:
        """
        Generates a list of [lon, lat] coordinates forming a closed circle polygon.
        """
        coordinates: List[List[float]] = []
        for i in range(num_points):
            bearing = (360.0 / num_points) * i
            pt = self.destination_point(lat, lon, radius_km, bearing)
            coordinates.append([round(pt[0], 5), round(pt[1], 5)])
        # Close the polygon loop
        coordinates.append(coordinates[0])
        return coordinates

    def generate_cone_of_uncertainty(
        self,
        cyclone_id: str,
        track_points: List[Dict[str, Any]]
    ) -> ForecastConeResponse:
        """
        Generates a smooth tapering GeoJSON polygon for the forecast cone of uncertainty.
        `track_points` is a list of dicts with keys: lat, lon, uncertainty_radius_km.
        """
        if not track_points:
            # Fallback default cone along South Andhra coast
            fallback_coords = [
                [82.1, 14.5], [81.8, 14.8], [81.2, 15.3], [80.3, 15.9],
                [79.4, 16.5], [78.7, 17.1], [79.5, 16.9], [80.7, 16.3],
                [81.6, 15.7], [82.3, 15.1], [82.1, 14.5]
            ]
            return ForecastConeResponse(
                cyclone_id=cyclone_id,
                type="FeatureCollection",
                features=[
                    ConeFeature(
                        type="Feature",
                        properties={
                            "cyclone_id": cyclone_id,
                            "description": "Default Cone of Uncertainty",
                            "confidence_interval": "67%"
                        },
                        geometry=ConeGeometry(type="Polygon", coordinates=[fallback_coords])
                    )
                ]
            )

        left_boundary: List[List[float]] = []
        right_boundary: List[List[float]] = []

        for i, pt in enumerate(track_points):
            lat = pt.get("lat", 14.5)
            lon = pt.get("lon", 82.1)
            radius = max(float(pt.get("uncertainty_radius_km", 25.0) or 25.0), 15.0)

            # Determine track direction bearing to compute perpendicular offsets
            if i < len(track_points) - 1:
                next_pt = track_points[i + 1]
                bearing = math.degrees(math.atan2(
                    math.radians(next_pt.get("lon", lon) - lon),
                    math.radians(next_pt.get("lat", lat) - lat)
                )) % 360.0
            elif i > 0:
                prev_pt = track_points[i - 1]
                bearing = math.degrees(math.atan2(
                    math.radians(lon - prev_pt.get("lon", lon)),
                    math.radians(lat - prev_pt.get("lat", lat))
                )) % 360.0
            else:
                bearing = 315.0  # Default North-West movement

            # Left perpendicular (-90 deg) and Right perpendicular (+90 deg)
            left_pt = self.destination_point(lat, lon, radius, (bearing - 90.0) % 360.0)
            right_pt = self.destination_point(lat, lon, radius, (bearing + 90.0) % 360.0)

            left_boundary.append([round(left_pt[0], 5), round(left_pt[1], 5)])
            right_boundary.append([round(right_pt[0], 5), round(right_pt[1], 5)])

        # Semi-circular cap around final forecast point
        last_pt = track_points[-1]
        last_lat = last_pt.get("lat", 16.7)
        last_lon = last_pt.get("lon", 79.1)
        last_radius = max(float(last_pt.get("uncertainty_radius_km", 90.0) or 90.0), 30.0)
        
        cap_points: List[List[float]] = []
        # Calculate forward bearing of last segment
        if len(track_points) > 1:
            prev = track_points[-2]
            fwd_bearing = math.degrees(math.atan2(
                math.radians(last_lon - prev.get("lon", last_lon)),
                math.radians(last_lat - prev.get("lat", last_lat))
            )) % 360.0
        else:
            fwd_bearing = 315.0

        for angle_offset in range(-90, 91, 15):
            cap_angle = (fwd_bearing + angle_offset) % 360.0
            pt = self.destination_point(last_lat, last_lon, last_radius, cap_angle)
            cap_points.append([round(pt[0], 5), round(pt[1], 5)])

        # Construct closed polygon: Left boundary -> Cap -> Right boundary (reversed) -> Close
        cone_coords = left_boundary + cap_points + list(reversed(right_boundary))
        cone_coords.append(cone_coords[0])  # Close loop

        max_radius = max(float(p.get("uncertainty_radius_km", 0.0) or 0.0) for p in track_points)

        return ForecastConeResponse(
            cyclone_id=cyclone_id,
            type="FeatureCollection",
            features=[
                ConeFeature(
                    type="Feature",
                    properties={
                        "cyclone_id": cyclone_id,
                        "description": f"Forecast Cone of Uncertainty ({len(track_points)} track points)",
                        "max_uncertainty_radius_km": round(max_radius, 1),
                        "confidence_interval": "67%",
                        "track_points_count": len(track_points)
                    },
                    geometry=ConeGeometry(
                        type="Polygon",
                        coordinates=[cone_coords]
                    )
                )
            ]
        )

    def generate_wind_buffers(
        self,
        cyclone_id: str,
        current_lat: float,
        current_lon: float,
        max_wind_kmh: float = 165.0
    ) -> WindBufferResponse:
        """
        Generates standard multi-tier wind hazard buffers:
        1. 34-knot (Gale force, 63 km/h+) - Outer Swath (~180-240 km radius)
        2. 50-knot (Storm force, 92 km/h+) - Middle Swath (~100-140 km radius)
        3. 64-knot (Hurricane force, 118 km/h+) - Core Swath (~45-70 km radius)
        """
        # Scale radii proportionally based on maximum sustained wind speed
        intensity_factor = max(max_wind_kmh / 150.0, 0.7)
        r_64kt = round(55.0 * intensity_factor, 1)
        r_50kt = round(110.0 * intensity_factor, 1)
        r_34kt = round(200.0 * intensity_factor, 1)

        buffer_configs = [
            {
                "wind_speed_kt": 34,
                "wind_speed_kmh": 63,
                "radius_km": r_34kt,
                "severity": "GALE_FORCE",
                "label": f"34-Knot Wind Buffer ({r_34kt} km)",
                "color": "#facc15",  # Yellow
                "opacity": 0.25
            },
            {
                "wind_speed_kt": 50,
                "wind_speed_kmh": 92,
                "radius_km": r_50kt,
                "severity": "STORM_FORCE",
                "label": f"50-Knot Wind Buffer ({r_50kt} km)",
                "color": "#fb923c",  # Orange
                "opacity": 0.35
            },
            {
                "wind_speed_kt": 64,
                "wind_speed_kmh": 118,
                "radius_km": r_64kt,
                "severity": "HURRICANE_FORCE",
                "label": f"64-Knot Core Hurricane Buffer ({r_64kt} km)",
                "color": "#ef4444",  # Red
                "opacity": 0.50
            }
        ]

        features: List[WindBufferFeature] = []
        for cfg in buffer_configs:
            circle_coords = self.create_circle_polygon(
                lat=current_lat,
                lon=current_lon,
                radius_km=cfg["radius_km"]
            )
            features.append(
                WindBufferFeature(
                    type="Feature",
                    properties={
                        "cyclone_id": cyclone_id,
                        "wind_speed_kt": cfg["wind_speed_kt"],
                        "wind_speed_kmh": cfg["wind_speed_kmh"],
                        "radius_km": cfg["radius_km"],
                        "severity": cfg["severity"],
                        "label": cfg["label"],
                        "color": cfg["color"],
                        "opacity": cfg["opacity"]
                    },
                    geometry=ConeGeometry(
                        type="Polygon",
                        coordinates=[circle_coords]
                    )
                )
            )

        return WindBufferResponse(
            cyclone_id=cyclone_id,
            type="FeatureCollection",
            features=features
        )


geometry_engine = GeometryEngine()
