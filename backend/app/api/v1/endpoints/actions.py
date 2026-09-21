"""
Emergency Action SOP & Triage Endpoints
Owner: Krishna
"""

from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import ActionItem
from app.services.action_engine import action_engine

router = APIRouter()


class StatusUpdateRequest(BaseModel):
    action_id: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED


@router.get("/recommendations/{cyclone_id}", response_model=List[ActionItem])
async def get_action_recommendations(cyclone_id: str):
    """
    Returns prioritized emergency actions and department-assigned SOP items.
    """
    return action_engine.get_action_items(cyclone_id)


@router.post("/update-status")
async def update_action_status(payload: StatusUpdateRequest):
    """
    Updates the operational status of an action item.
    """
    success = action_engine.update_action_status(payload.action_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Action item ID not found")
    return {"status": "success", "action_id": payload.action_id, "updated_to": payload.status}
