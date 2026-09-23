"""
Backend Action SOP & Triage Trigger Engine
Owner: Krishna
"""

from typing import List
from app.schemas.models import ActionItem


class ActionEngine:
    """
    Generates rule-based SOP actions and tracks triage dispatch status.
    """

    def __init__(self):
        # In-memory action database for active responses
        self.actions_db: List[ActionItem] = [
            ActionItem(
                id="ACT-001",
                priority="HIGH",
                phase="PRE_LANDFALL",
                sector="Evacuation",
                instruction="Evacuate 45,000 residents from low-lying coastal villages (0-5km) in Nellore.",
                status="IN_PROGRESS",
                assigned_agency="NDRF Battalion 10 & District Revenue"
            ),
            ActionItem(
                id="ACT-002",
                priority="HIGH",
                phase="PRE_LANDFALL",
                sector="Medical",
                instruction="Deliver diesel generator backup & oxygen supplies to 8 high-risk hospitals.",
                status="COMPLETED",
                assigned_agency="District Medical & Health Office"
            ),
            ActionItem(
                id="ACT-003",
                priority="HIGH",
                phase="PRE_LANDFALL",
                sector="Shelter",
                instruction="Activate 42 cyclone relief shelters with 72-hour dry food and potable water supplies.",
                status="IN_PROGRESS",
                assigned_agency="Civil Supplies & SDRF"
            ),
            ActionItem(
                id="ACT-004",
                priority="MEDIUM",
                phase="LANDFALL",
                sector="Power",
                instruction="Pre-emptively shut down secondary electrical grids in vulnerable storm-surge zones.",
                status="PENDING",
                assigned_agency="State Electricity Distribution Company"
            ),
            ActionItem(
                id="ACT-005",
                priority="MEDIUM",
                phase="POST_LANDFALL",
                sector="Rescue",
                instruction="Deploy 12 NDRF search and rescue boat teams along coastal river mouths.",
                status="PENDING",
                assigned_agency="NDRF & Indian Coast Guard"
            )
        ]

    def get_action_items(self, cyclone_id: str) -> List[ActionItem]:
        return self.actions_db

    def update_action_status(self, action_id: str, new_status: str) -> bool:
        for item in self.actions_db:
            if item.id == action_id:
                item.status = new_status
                return True
        return False


action_engine = ActionEngine()
