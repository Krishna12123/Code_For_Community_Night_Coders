"""
Disaster Situation Report & PDF Generation Engine
Owner: Krishna (Backend & Risk Engine Architect)
Consolidates Vikash's Geospatial/AI models and Krishna's Risk/Action models into an official downloadable SITREP.
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)

from app.schemas.models import RiskAssessment, CycloneData, ActionItem, AIBriefingResponse


class SituationReportEngine:
    """
    Generates official Incident Situation Reports (SITREPs) in PDF and structured JSON formats.
    """

    def generate_pdf_report(
        self,
        cyclone_id: str,
        storm_data: Optional[CycloneData],
        risk_assessment: RiskAssessment,
        ai_briefing: Optional[AIBriefingResponse],
        actions: List[ActionItem],
        gee_evidence: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Builds an executive, multi-page, formatted PDF disaster situation report.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom palette & typography
        header_title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0f172a'),
            alignment=1  # Centered
        )
        
        sub_title_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#dc2626'),
            alignment=1
        )
        
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#475569')
        )
        
        meta_val_style = ParagraphStyle(
            'MetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0f172a')
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#334155')
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.white
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#1e293b')
        )

        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor('#0f172a')
        )

        story = []

        # 1. Official Header
        story.append(Paragraph("NATIONAL CYCLONE DISASTER MANAGEMENT COMMAND", header_title_style))
        story.append(Paragraph("OFFICIAL EMERGENCY INCIDENT SITUATION REPORT (SITREP)", sub_title_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#dc2626'), spaceAfter=8))

        # 2. Metadata Banner Table
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        threat_color_map = {
            "RED": "#dc2626",
            "ORANGE": "#ea580c",
            "YELLOW": "#ca8a04",
            "GREEN": "#16a34a"
        }
        threat_bg = threat_color_map.get(risk_assessment.threat_level, "#dc2626")

        storm_name = storm_data.name if storm_data else "Cyclone Vardah-II"
        storm_cat = f"Category {storm_data.category}" if storm_data else "Category 3"
        max_wind = f"{int(storm_data.max_sustained_wind_kmh)} km/h" if storm_data else "165 km/h"
        central_press = f"{storm_data.central_pressure_mb or 960} mb" if storm_data else "960 mb"
        eye_pos = f"{storm_data.current_position.lat:.2f}°N, {storm_data.current_position.lon:.2f}°E" if storm_data else "14.50°N, 82.10°E"

        meta_data = [
            [
                Paragraph("<b>INCIDENT ID:</b>", meta_label_style),
                Paragraph(cyclone_id, meta_val_style),
                Paragraph("<b>STORM NAME:</b>", meta_label_style),
                Paragraph(f"{storm_name} ({storm_cat})", meta_val_style),
                Paragraph("<b>THREAT LEVEL:</b>", meta_label_style),
                Paragraph(f"<font color='{threat_bg}'><b>{risk_assessment.threat_level} ALERT</b></font>", meta_val_style)
            ],
            [
                Paragraph("<b>REPORT TIME:</b>", meta_label_style),
                Paragraph(now_utc, meta_val_style),
                Paragraph("<b>CURRENT EYE:</b>", meta_label_style),
                Paragraph(eye_pos, meta_val_style),
                Paragraph("<b>LANDFALL ETA:</b>", meta_label_style),
                Paragraph(f"T-Minus {risk_assessment.landfall_eta_hours} Hours", meta_val_style)
            ],
            [
                Paragraph("<b>MAX WINDS:</b>", meta_label_style),
                Paragraph(max_wind, meta_val_style),
                Paragraph("<b>CENTRAL PRESS:</b>", meta_label_style),
                Paragraph(central_press, meta_val_style),
                Paragraph("<b>EXPOSED POP:</b>", meta_label_style),
                Paragraph(f"<b>{risk_assessment.total_population_at_risk:,}</b>", meta_val_style)
            ]
        ]

        meta_table = Table(meta_data, colWidths=[70, 110, 75, 125, 75, 85])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # 3. Executive Summary & Gemini AI Briefing
        story.append(Paragraph("1. EXECUTIVE DISASTER SUMMARY & SITUATIONAL ASSESSMENT", h2_style))
        summary_text = risk_assessment.executive_summary
        if ai_briefing and ai_briefing.executive_summary:
            summary_text = ai_briefing.executive_summary
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 8))

        # 4. District Exposure & Vulnerability Table
        story.append(Paragraph("2. DISTRICT MULTI-HAZARD EXPOSURE & IMPACT METRICS", h2_style))
        
        district_rows = [
            [
                Paragraph("<b>District</b>", table_header_style),
                Paragraph("<b>Risk Score</b>", table_header_style),
                Paragraph("<b>Threat</b>", table_header_style),
                Paragraph("<b>Flooded Area</b>", table_header_style),
                Paragraph("<b>Hospitals</b>", table_header_style),
                Paragraph("<b>Shelters</b>", table_header_style),
                Paragraph("<b>Population Exposed</b>", table_header_style)
            ]
        ]

        for d in risk_assessment.high_risk_districts:
            level_color = threat_color_map.get(d.risk_level, "#334155")
            district_rows.append([
                Paragraph(f"<b>{d.district_name}</b>", table_cell_bold),
                Paragraph(f"{d.risk_score:.1f} / 100", table_cell_style),
                Paragraph(f"<font color='{level_color}'><b>{d.risk_level}</b></font>", table_cell_style),
                Paragraph(f"{d.flooded_area_sq_km:.1f} km²", table_cell_style),
                Paragraph(f"{d.vulnerable_hospitals} at risk", table_cell_style),
                Paragraph(f"{d.shelters_available} active", table_cell_style),
                Paragraph(f"{d.population_exposed:,}", table_cell_style)
            ])

        district_table = Table(
            district_rows,
            colWidths=[85, 65, 55, 75, 75, 65, 120]
        )
        district_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(district_table)
        story.append(Spacer(1, 10))

        # 5. Geospatial Evidence & Earth Observation Data
        story.append(Paragraph("3. SATELLITE RADAR & EARTH OBSERVATION EVIDENCE (GEE)", h2_style))
        sar_status = "Sentinel-1 SAR GRD Backscatter (COPERNICUS/S1_GRD) active"
        gpm_status = "NASA GPM IMERG 24-hr Accumulation (NASA/GPM_L3/IMERG_V07) active"
        total_flood_area = sum(d.flooded_area_sq_km for d in risk_assessment.high_risk_districts)
        
        evidence_p = (
            f"• <b>Flood Inundation Extent:</b> Estimated {total_flood_area:.1f} km² inundated terrain based on Sentinel-1 SAR change detection.<br/>"
            f"• <b>Precipitation Anomaly:</b> High-intensity core localized over coastal Andhra Pradesh corridor.<br/>"
            f"• <b>Sensors & Feeds:</b> {sar_status} &amp; {gpm_status}."
        )
        story.append(Paragraph(evidence_p, body_style))
        story.append(Spacer(1, 10))

        # 6. Operational Emergency Action SOP Matrix
        story.append(Paragraph("4. OPERATIONAL EMERGENCY SOP & TRIAGE CHECKLIST", h2_style))
        
        action_rows = [
            [
                Paragraph("<b>ID / Priority</b>", table_header_style),
                Paragraph("<b>Phase</b>", table_header_style),
                Paragraph("<b>Sector</b>", table_header_style),
                Paragraph("<b>Emergency Operational Instruction</b>", table_header_style),
                Paragraph("<b>Agency</b>", table_header_style),
                Paragraph("<b>Status</b>", table_header_style)
            ]
        ]

        status_color_map = {
            "COMPLETED": "#16a34a",
            "IN_PROGRESS": "#ea580c",
            "PENDING": "#64748b"
        }

        for act in actions:
            p_color = "#dc2626" if act.priority == "HIGH" else "#ca8a04" if act.priority == "MEDIUM" else "#64748b"
            s_color = status_color_map.get(act.status, "#64748b")
            action_rows.append([
                Paragraph(f"<font color='{p_color}'><b>[{act.priority}]</b></font><br/>{act.id}", table_cell_style),
                Paragraph(act.phase.replace("_", " "), table_cell_style),
                Paragraph(f"<b>{act.sector}</b>", table_cell_style),
                Paragraph(act.instruction, table_cell_style),
                Paragraph(act.assigned_agency or "NDRF / Local Admin", table_cell_style),
                Paragraph(f"<font color='{s_color}'><b>{act.status.replace('_', ' ')}</b></font>", table_cell_style)
            ])

        action_table = Table(
            action_rows,
            colWidths=[65, 75, 60, 175, 95, 70]
        )
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(action_table)
        story.append(Spacer(1, 12))

        # 7. Disclaimers & Verification
        footer_text = (
            "<i>CONFIDENTIAL &amp; PROPRIETARY — Generated automatically by Cyclone Risk Assessment &amp; "
            "Action Engine Command Platform. Field reconnaissance teams and local district collectors must "
            "verify ground conditions before re-entry into evacuated zones.</i>"
        )
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=4))
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=6.5, leading=8.5, textColor=colors.HexColor('#64748b'))))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def generate_json_report(
        self,
        cyclone_id: str,
        storm_data: Optional[CycloneData],
        risk_assessment: RiskAssessment,
        ai_briefing: Optional[AIBriefingResponse],
        actions: List[ActionItem]
    ) -> Dict[str, Any]:
        """
        Consolidates complete disaster situation metrics into structured JSON.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "report_id": f"SITREP-{cyclone_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
            "generated_at": now_iso,
            "cyclone_id": cyclone_id,
            "storm_telemetry": storm_data.model_dump() if storm_data else {
                "cyclone_id": cyclone_id,
                "name": "Cyclone Vardah-II",
                "category": 3,
                "max_sustained_wind_kmh": 165.0,
                "central_pressure_mb": 960.0
            },
            "risk_assessment": risk_assessment.model_dump(),
            "ai_situation_briefing": ai_briefing.model_dump() if ai_briefing else None,
            "operational_actions": [a.model_dump() for a in actions],
            "metadata": {
                "security_classification": "OFFICIAL_DISASTER_SITREP",
                "system": "Cyclone Risk Assessment & Action Engine Backend",
                "version": "1.0.0"
            }
        }


report_engine = SituationReportEngine()
