"""
Geospatial AI Domain - Gemini Disaster Reasoning & Multimodal Advisor
Owner: Vikash
"""

import os
from typing import Dict, Any
from google import genai
from pydantic import ValidationError
from geospatial_ai.schemas import AdvisoryBriefing, CycloneData, GeospatialEvidence

class GeminiDisasterAdvisor:
    """
    Orchestrates Gemini to analyze cyclone parameters, flood metrics,
    and exposure data to produce structured disaster briefings and action priorities.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Ensure we use Gemini 3.7 Flash as requested, but allow environment override.
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

    def generate_situation_briefing(
        self, 
        storm_data: CycloneData, 
        exposure_data: Dict[str, Any],
        geospatial_evidence: GeospatialEvidence
    ) -> AdvisoryBriefing:
        """
        Generates executive disaster briefing and emergency SOP checklist.
        """
        if self.api_key:
            try:
                client = genai.Client(api_key=self.api_key)
                prompt = f"""
                You are a Senior Cyclone Disaster Response Commander. Analyze this real-time cyclone and exposure data:
                
                Storm: {storm_data.model_dump_json()}
                Geospatial Evidence: {geospatial_evidence.model_dump_json()}
                Exposure & Vulnerability: {exposure_data}

                CRITICAL RULES:
                - Do NOT invent numerical measurements.
                - Use ONLY the supplied evidence.
                - Distinguish observations from recommendations.
                - Identify missing information in the limitations array.
                - Do not claim an official evacuation order exists unless stated in the data.
                - Respond ONLY in valid JSON matching the requested schema.
                """
                
                # We use structured output feature of GenAI SDK if supported, otherwise we just prompt for JSON.
                # Since GenAI SDK supports response_schema with Pydantic:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": AdvisoryBriefing,
                    }
                )
                
                try:
                    return AdvisoryBriefing.model_validate_json(response.text)
                except ValidationError as e:
                    print(f"[Gemini] Structured output validation failed: {e}")
                    # Fallthrough to fallback
            except Exception as e:
                print(f"[Gemini] API call failed: {e}. Using fallback briefing.")

        # Strict unavailable/error fallback state
        return AdvisoryBriefing(
            executive_summary="AI briefing is currently unavailable due to missing API key or connection failure. No automated advisory can be generated.",
            threat_level="UNKNOWN",
            high_risk_districts=[],
            critical_actions=[],
            evidence_used=[],
            limitations=["AI services are offline or unreachable. No live analysis available."],
            mode="unavailable"
        )


if __name__ == "__main__":
    from geospatial_ai.schemas import Point
    import datetime
    
    advisor = GeminiDisasterAdvisor()
    now = datetime.datetime.now(datetime.timezone.utc)
    mock_storm = CycloneData(
        cyclone_id="CYC-TEST",
        name="Test Cyclone",
        source="synthetic_fixture",
        category=3,
        max_sustained_wind_kmh=150.0,
        current_position=Point(lat=10.0, lon=80.0, recorded_at=now)
    )
    from geospatial_ai.gee.gee_pipeline import GEEPipeline
    mock_evidence = GEEPipeline().generate_evidence([80.0, 10.0, 81.0, 11.0], "today")
    
    briefing = advisor.generate_situation_briefing(
        mock_storm,
        {"total_population_at_risk": 1850000},
        mock_evidence
    )
    print("Gemini Advisory Output:\n", briefing.model_dump_json(indent=2))
