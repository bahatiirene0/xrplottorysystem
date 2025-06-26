from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from . import db as gamification_db
from .models import (
    AchievementDefinition, UserAchievement, UserAchievementResponse, UserLoyalty,
    AchievementDefinitionCreate, AchievementDefinitionUpdate # For admin endpoints if added later
)
from auth.dependencies import get_current_user_from_token
from auth.models import TokenData
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Public/User-Facing Endpoints ---

@router.get("/achievements/definitions", response_model=List[AchievementDefinition], summary="List all active achievement definitions")
async def list_active_achievement_definitions():
    """
    Provides a list of all achievements that can currently be earned by users.
    """
    try:
        definitions = gamification_db.get_all_achievement_definitions(active_only=True)
        return definitions
    except Exception as e:
        logger.exception("Error fetching achievement definitions.")
        raise HTTPException(status_code=500, detail="Could not retrieve achievement definitions.")

@router.get("/achievements/my", response_model=List[UserAchievementResponse], summary="List achievements earned by the current user")
async def list_my_earned_achievements(
    token_data: TokenData = Depends(get_current_user_from_token)
):
    """
    Retrieves all achievements that the currently authenticated user has earned.
    """
    user_wallet = token_data.wallet_address
    if not user_wallet:
         raise HTTPException(status_code=401, detail="Could not identify user from token.")
    try:
        user_achievements = gamification_db.get_user_achievements(user_wallet)
        return user_achievements # UserAchievementResponse is compatible with UserAchievement
    except Exception as e:
        logger.exception(f"Error fetching achievements for user {user_wallet}.")
        raise HTTPException(status_code=500, detail="Could not retrieve user's achievements.")

@router.get("/loyalty/my_status", response_model=UserLoyalty, summary="Get current user's loyalty status")
async def get_my_loyalty_status(
    token_data: TokenData = Depends(get_current_user_from_token)
):
    """
    Retrieves the loyalty points and status for the currently authenticated user.
    """
    user_wallet = token_data.wallet_address
    if not user_wallet:
         raise HTTPException(status_code=401, detail="Could not identify user from token.")
    try:
        loyalty_status = gamification_db.get_or_create_user_loyalty(user_wallet)
        if not loyalty_status:
            # This should ideally not happen if get_or_create is robust
            logger.error(f"Failed to get or create loyalty status for user {user_wallet}")
            raise HTTPException(status_code=500, detail="Could not retrieve user's loyalty status.")
        return loyalty_status
    except Exception as e:
        logger.exception(f"Error fetching loyalty status for user {user_wallet}.")
        raise HTTPException(status_code=500, detail="Could not retrieve user's loyalty status.")

# --- Admin Endpoints (Example - Not fully part of current user-facing plan but good for completeness) ---
# These would need admin-level authentication

@router.post("/admin/achievements/definitions", response_model=AchievementDefinition, status_code=201, summary="ADMIN: Create new achievement definition", include_in_schema=False)
async def admin_create_achievement_definition(
    definition_data: AchievementDefinitionCreate,
    # TODO: Add admin authentication dependency here
    # current_admin: User = Depends(get_current_admin_user)
):
    # For now, accessible if uncommented and admin auth is added
    # if not is_admin(current_admin):
    #     raise HTTPException(status_code=403, detail="Not authorized")
    try:
        definition = gamification_db.create_achievement_definition(definition_data)
        if not definition:
            raise HTTPException(status_code=500, detail="Failed to create achievement definition.")
        return definition
    except Exception as e:
        logger.exception("Admin error creating achievement definition.")
        raise HTTPException(status_code=500, detail=f"Failed to create achievement definition: {str(e)}")

@router.put("/admin/achievements/definitions/{definition_id}", response_model=AchievementDefinition, summary="ADMIN: Update achievement definition", include_in_schema=False)
async def admin_update_achievement_definition(
    definition_id: str,
    update_data: AchievementDefinitionUpdate,
    # TODO: Add admin authentication dependency here
):
    try:
        updated_definition = gamification_db.update_achievement_definition(definition_id, update_data)
        if not updated_definition:
            raise HTTPException(status_code=404, detail="Achievement definition not found or update failed.")
        return updated_definition
    except Exception as e:
        logger.exception(f"Admin error updating achievement definition {definition_id}.")
        raise HTTPException(status_code=500, detail=f"Failed to update achievement definition: {str(e)}")

# Add this router to app.py
# from gamification.router import router as gamification_router
# app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"])
