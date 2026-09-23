"""
Emergency Action SOP & Triage API Router
Owner: Krishna (Backend & Risk Engine Architect)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.models import ActionItem, StatusUpdateRequest
from app.db.database import get_db
from app.services.action_engine import action_engine
from app.services.risk_engine import risk_engine
from app.db import models

router = APIRouter()


@router.get("/recommendations/{cyclone_id}", response_model=List[ActionItem])
async def get_action_recommendations(cyclone_id: str, db: Session = Depends(get_db)):
    """
    Returns prioritized emergency actions and department-assigned SOP items
    dynamically mapped to threat tiers.
    """
    # 1. Fetch risk threat level
    exposure = risk_engine.calculate_exposure_from_db(db=db, cyclone_id=cyclone_id)
    red_districts = [d.district_name for d in exposure.high_risk_districts if d.risk_level == "RED"]

    # 2. Retrieve or generate rule-based actions
    actions = action_engine.get_or_create_actions_for_cyclone(
        db=db,
        cyclone_id=cyclone_id,
        threat_level=exposure.threat_level,
        red_districts=red_districts
    )

    return actions


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

    updated = action_engine.update_action_status(
        db=db,
        action_id=payload.action_id,
        new_status=payload.status
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Action item '{payload.action_id}' not found"
        )

    return {
        "status": "success",
        "action_id": payload.action_id,
        "updated_to": payload.status,
        "message": f"Action {payload.action_id} status updated to {payload.status}"
    }
