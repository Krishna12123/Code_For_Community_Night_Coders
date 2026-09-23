"""
Backend Multi-Hazard Composite Risk & Exposure Engine
Owner: Krishna (Backend & Risk Engine Architect)
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.schemas.models import RiskAssessment, DistrictRisk
from app.services.geometry_engine import geometry_engine
from app.db import models


class RiskEngine:
    """
    Computes spatial exposure (population, hospitals, flooded zone)
    and calculates composite multi-hazard risk scores based on mathematical modeling.
    """

    # Multi-hazard weights (sum = 1.0)
    W_WIND = 0.35
    W_FLOOD = 0.25
    W_SURGE = 0.20
    W_VULN = 0.20

    def calculate_district_composite_risk(
        self,
        district_name: str,
        dist_lat: float,
        dist_lon: float,
        storm_lat: float,
        storm_lon: float,
        max_wind_kmh: float,
        flooded_area_sq_km: float,
        vulnerable_hospitals: int,
        total_hospitals: int,
        baseline_pop: int
    ) -> DistrictRisk:
        """
        Calculates the multi-hazard risk score for a single district.
        Risk Score = w1*Wind + w2*Flood + w3*Surge + w4*Vulnerability
        """
        distance_km = geometry_engine.haversine_distance_km(dist_lat, dist_lon, storm_lat, storm_lon)

        # 1. Wind Hazard Score (0-100)
        if distance_km <= 65.0:
            wind_hazard = min(100.0, 85.0 + (max_wind_kmh / 200.0) * 15.0)
        elif distance_km <= 130.0:
            wind_hazard = 65.0 + (130.0 - distance_km) / 65.0 * 20.0
        elif distance_km <= 230.0:
            wind_hazard = 35.0 + (230.0 - distance_km) / 100.0 * 25.0
        else:
            wind_hazard = max(5.0, 30.0 - (distance_km - 230.0) * 0.1)

        # 2. Flood Hazard Score (0-100)
        flood_hazard = min(100.0, (flooded_area_sq_km / 150.0) * 100.0)

        # 3. Storm Surge Hazard Score (0-100)
        # Coastal districts with high proximity to landfall receive higher surge scores
        if distance_km <= 100.0:
            surge_hazard = min(100.0, 75.0 + (100.0 - distance_km) * 0.25)
        elif distance_km <= 200.0:
            surge_hazard = max(20.0, 50.0 - (distance_km - 100.0) * 0.3)
        else:
            surge_hazard = 15.0

        # 4. Vulnerability Index (0-100)
        hosp_ratio = (vulnerable_hospitals / max(total_hospitals, 1))
        vuln_index = min(100.0, hosp_ratio * 70.0 + 30.0)

        # Composite Multi-Hazard Risk Index
        composite_score = (
            self.W_WIND * wind_hazard
            + self.W_FLOOD * flood_hazard
            + self.W_SURGE * surge_hazard
            + self.W_VULN * vuln_index
        )
        composite_score = round(min(100.0, max(0.0, composite_score)), 1)

        # Categorize Threat Level
        if composite_score >= 75.0:
            risk_level = "RED"
            exposure_fraction = 0.75
        elif composite_score >= 55.0:
            risk_level = "ORANGE"
            exposure_fraction = 0.50
        elif composite_score >= 30.0:
            risk_level = "YELLOW"
            exposure_fraction = 0.25
        else:
            risk_level = "GREEN"
            exposure_fraction = 0.05

        pop_exposed = int(baseline_pop * exposure_fraction)

        # Shelters available estimation
        shelters = max(10, int(vulnerable_hospitals * 4.5))

        return DistrictRisk(
            district_name=district_name,
            risk_score=composite_score,
            risk_level=risk_level,
            flooded_area_sq_km=round(flooded_area_sq_km, 1),
            vulnerable_hospitals=vulnerable_hospitals,
            shelters_available=shelters,
            population_exposed=pop_exposed
        )

    def calculate_exposure_from_db(
        self,
        db: Session,
        cyclone_id: str = "CYC-2026-01",
        storm_lat: float = 14.5,
        storm_lon: float = 82.1,
        max_wind_kmh: float = 165.0
    ) -> RiskAssessment:
        """
        Calculates dynamic exposure by reading all districts from the database
        and applying composite spatial risk scoring.
        """
        db_districts = db.query(models.DistrictDB).all()
        district_results: List[DistrictRisk] = []
        total_pop = 0
        max_score = 0.0

        for d in db_districts:
            d_lat = getattr(d, "lat", 14.5) or 14.5
            d_lon = getattr(d, "lon", 80.0) or 80.0
            base_pop = getattr(d, "baseline_population", 600000) or 600000
            tot_hosp = getattr(d, "total_hospitals", 10) or 10
            vuln_hosp = d.vulnerable_hospitals or int(tot_hosp * 0.6)
            flood_area = d.flooded_area_sq_km or 50.0

            d_risk = self.calculate_district_composite_risk(
                district_name=d.name,
                dist_lat=d_lat,
                dist_lon=d_lon,
                storm_lat=storm_lat,
                storm_lon=storm_lon,
                max_wind_kmh=max_wind_kmh,
                flooded_area_sq_km=flood_area,
                vulnerable_hospitals=vuln_hosp,
                total_hospitals=tot_hosp,
                baseline_pop=base_pop
            )

            # Update DB values for caching
            d.risk_score = d_risk.risk_score
            d.risk_level = d_risk.risk_level
            d.population_exposed = d_risk.population_exposed
            d.shelters_available = d_risk.shelters_available

            district_results.append(d_risk)
            total_pop += d_risk.population_exposed
            if d_risk.risk_score > max_score:
                max_score = d_risk.risk_score

        try:
            db.commit()
        except Exception:
            db.rollback()

        # Sort districts by risk score descending
        district_results.sort(key=lambda x: x.risk_score, reverse=True)

        # Global threat level
        if max_score >= 75.0:
            overall_threat = "RED"
        elif max_score >= 55.0:
            overall_threat = "ORANGE"
        elif max_score >= 30.0:
            overall_threat = "YELLOW"
        else:
            overall_threat = "GREEN"

        red_districts = [d.district_name for d in district_results if d.risk_level == "RED"]
        red_str = ", ".join(red_districts) if red_districts else "coastal regions"

        summary = (
            f"Severe Cyclonic Storm (Max wind {int(max_wind_kmh)} km/h) approaching coastline. "
            f"Estimated {total_pop:,} population within multi-hazard exposure zone. "
            f"Immediate mandatory evacuation and emergency protocols active for {red_str}."
        )

        return RiskAssessment(
            cyclone_id=cyclone_id,
            total_population_at_risk=total_pop,
            high_risk_districts=district_results,
            executive_summary=summary,
            threat_level=overall_threat,
            landfall_eta_hours=18
        )


risk_engine = RiskEngine()
