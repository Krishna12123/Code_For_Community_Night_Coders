"""
Emergency Action SOP & Triage API Router
Owner: Krishna
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.models import ActionItem, StatusUpdateRequest
from app.db.database import get_db
from app.db import models

router = APIRouter()


@router.get("/recommendations/{cyclone_id}", response_model=List[ActionItem])
async def get_action_recommendations(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Returns prioritized emergency actions and department-assigned SOP items.
    """
    db_actions = db.query(models.ActionItemDB).filter(models.ActionItemDB.cyclone_id == cyclone_id).all()
    
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
    
    # Fallback initial SOPs if none in database for this cyclone
    return [
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


@router.post("/update-status")
async def update_action_status(payload: StatusUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates the operational status of an action item (PENDING, IN_PROGRESS, COMPLETED).
    """
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of {valid_statuses}"
        )

    db_action = db.query(models.ActionItemDB).filter(models.ActionItemDB.id == payload.action_id).first()
    if not db_action:
        raise HTTPException(status_code=404, detail=f"Action item '{payload.action_id}' not found")

    db_action.status = payload.status
    db.commit()
    db.refresh(db_action)

    return {
        "status": "success",
        "action_id": payload.action_id,
        "updated_to": payload.status,
        "message": f"Action {payload.action_id} status updated to {payload.status}"
    }
