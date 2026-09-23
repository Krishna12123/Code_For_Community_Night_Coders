"""
Backend Action SOP & Emergency Triage Engine
Owner: Krishna (Backend & Risk Engine Architect)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.schemas.models import ActionItem
from app.db import models


class ActionEngine:
    """
    Generates rule-based Standard Operating Procedures (SOPs) based on
    calculated multi-hazard threat tiers and persists triage states in DB.
    """

    def generate_rule_based_actions(
        self,
        cyclone_id: str,
        threat_level: str = "RED",
        red_districts: Optional[List[str]] = None,
        landfall_eta_hours: int = 18
    ) -> List[ActionItem]:
        """
        Synthesizes standard disaster response protocols matching the threat severity.
        """
        districts_str = ", ".join(red_districts) if red_districts else "Nellore, Prakasam, Bapatla"

        if threat_level == "RED":
            return [
                ActionItem(
                    id="ACT-001",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Evacuation",
                    instruction=f"Execute mandatory evacuation of all coastal habitations within 0-5km zone across {districts_str}.",
                    status="IN_PROGRESS",
                    assigned_agency="NDRF Battalion 10 & District Revenue"
                ),
                ActionItem(
                    id="ACT-002",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Medical",
                    instruction="Deliver 100kVA diesel generator backup & oxygen supplies to frontline coastal hospitals.",
                    status="COMPLETED",
                    assigned_agency="District Medical & Health Office"
                ),
                ActionItem(
                    id="ACT-003",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Shelter",
                    instruction="Activate designated cyclone relief shelters with 72-hour dry food and potable water supplies.",
                    status="IN_PROGRESS",
                    assigned_agency="Civil Supplies & SDRF"
                ),
                ActionItem(
                    id="ACT-004",
                    priority="MEDIUM",
                    phase="LANDFALL",
                    sector="Power",
                    instruction="Pre-emptively shut down secondary electrical grids (33kV/11kV) in vulnerable storm-surge zones.",
                    status="PENDING",
                    assigned_agency="State Electricity Distribution Company"
                ),
                ActionItem(
                    id="ACT-005",
                    priority="MEDIUM",
                    phase="POST_LANDFALL",
                    sector="Rescue",
                    instruction="Deploy 12 NDRF search and rescue boat teams with chainsaw equipment along coastal river mouths.",
                    status="PENDING",
                    assigned_agency="NDRF & Indian Coast Guard"
                )
            ]
        elif threat_level == "ORANGE":
            return [
                ActionItem(
                    id="ACT-001",
                    priority="HIGH",
                    phase="PRE_LANDFALL",
                    sector="Evacuation",
                    instruction=f"Issue voluntary evacuation advisories for low-lying and kutcha house residents in {districts_str}.",
                    status="IN_PROGRESS",
                    assigned_agency="District Revenue & Police"
                ),
                ActionItem(
                    id="ACT-002",
                    priority="MEDIUM",
                    phase="PRE_LANDFALL",
                    sector="Shelter",
                    instruction="Pre-position medical supplies and water tankers at primary cyclone shelters.",
                    status="PENDING",
                    assigned_agency="Civil Supplies Department"
                ),
                ActionItem(
                    id="ACT-003",
                    priority="MEDIUM",
                    phase="LANDFALL",
                    sector="Power",
                    instruction="Place emergency substation repair crews on 1-hour standby.",
                    status="PENDING",
                    assigned_agency="State Electricity Distribution Company"
                )
            ]
        else:
            return [
                ActionItem(
                    id="ACT-001",
                    priority="LOW",
                    phase="PRE_LANDFALL",
                    sector="Advisory",
                    instruction="Broadcast coastal weather bulletins and advise fishermen not to venture into deep sea.",
                    status="IN_PROGRESS",
                    assigned_agency="State Disaster Management Authority"
                )
            ]

    def get_or_create_actions_for_cyclone(
        self,
        db: Session,
        cyclone_id: str,
        threat_level: str = "RED",
        red_districts: Optional[List[str]] = None
    ) -> List[ActionItem]:
        """
        Retrieves existing actions from DB or generates and seeds rule-based actions.
        """
        db_actions = db.query(models.ActionItemDB).filter(
            models.ActionItemDB.cyclone_id == cyclone_id
        ).all()

        if db_actions:
            return [
                ActionItem(
                    id=a.id,
                    priority=a.priority,
                    phase=a.phase,
                    sector=a.sector,
                    instruction=a.instruction,
                    status=a.status,
                    assigned_agency=a.assigned_agency
                )
                for a in db_actions
            ]

        # Generate and seed into DB
        generated = self.generate_rule_based_actions(
            cyclone_id=cyclone_id,
            threat_level=threat_level,
            red_districts=red_districts
        )

        for item in generated:
            db_item = models.ActionItemDB(
                id=item.id,
                cyclone_id=cyclone_id,
                priority=item.priority,
                phase=item.phase,
                sector=item.sector,
                instruction=item.instruction,
                status=item.status,
                assigned_agency=item.assigned_agency
            )
            db.add(db_item)

        try:
            db.commit()
        except Exception:
            db.rollback()

        return generated

    def update_action_status(self, db: Session, action_id: str, new_status: str) -> bool:
        """
        Updates the status of an action in the database.
        """
        db_action = db.query(models.ActionItemDB).filter(
            models.ActionItemDB.id == action_id
        ).first()

        if not db_action:
            return False

        db_action.status = new_status
        db_action.updated_at = datetime.now(timezone.utc)
        try:
            db.commit()
            db.refresh(db_action)
            return True
        except Exception:
            db.rollback()
            return False


action_engine = ActionEngine()
