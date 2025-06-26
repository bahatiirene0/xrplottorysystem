from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class AchievementEventType(str, Enum):
    TICKET_PURCHASE = "ticket_purchase" # data: {"count": int, "category_id": Optional[str]}
    DRAW_WIN = "draw_win"               # data: {"prize_amount": float, "tier_name": str, "category_id": str}
    REFERRAL_SUCCESS = "referral_success" # data: {"count": int}
    SYNDICATE_JOIN = "syndicate_join"     # data: {"syndicate_id": str}
    SYNDICATE_WIN = "syndicate_win"       # data: {"syndicate_id": str, "prize_amount": float}
    # Add more event types as needed

class AchievementCriteriaValue(BaseModel):
    count: Optional[int] = Field(None, gt=0, description="Number of times the event must occur.")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount for an event (e.g., prize won, tickets purchased value).")
    category_id: Optional[str] = Field(None, description="Specific lottery category ID for the event.")
    tier_name: Optional[str] = Field(None, description="Specific prize tier name for a win event.")
    # Other specific criteria fields can be added

class AchievementCriteria(BaseModel):
    event_type: AchievementEventType = Field(..., description="The type of event that triggers progress or unlocks this achievement.")
    conditions: AchievementCriteriaValue = Field(..., description="The specific conditions that must be met for this event type.")
    # Example: event_type=TICKET_PURCHASE, conditions={"count": 10, "category_id": "some_cat_id"}
    # Example: event_type=DRAW_WIN, conditions={"min_amount": 100.0}

class AchievementDefinition(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the achievement (e.g., 'First Win!', 'Serial Player')")
    description: str = Field(..., max_length=250, description="Description of how to earn the achievement.")
    icon_url: Optional[str] = Field(None, description="URL to an icon representing the achievement.")

    criteria: List[AchievementCriteria] = Field(..., min_items=1, description="A list of criteria that must ALL be met to earn the achievement. For simpler achievements, this list will have one item.")
    # For multi-step achievements, criteria could be ordered, or progress tracked per criterion.
    # For now, assume all criteria must be met (AND logic). OR logic or step-based would require more complex progress tracking.

    points_reward: int = Field(default=0, ge=0, description="Loyalty points awarded when this achievement is unlocked.")
    is_active: bool = Field(True, description="Whether this achievement can currently be earned.")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}


class UserAchievementProgress(BaseModel):
    # Stores progress for a single criterion if an achievement has multiple criteria or requires multiple events for one criterion
    criterion_index: int # Index into AchievementDefinition.criteria list
    current_count: Optional[int] = 0
    current_amount_sum: Optional[float] = 0.0
    # other progress trackers as needed

class UserAchievement(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID")
    user_wallet_address: str = Field(..., index=True)
    achievement_definition_id: str = Field(...)

    name: str # Denormalized from AchievementDefinition for easy display
    description: str # Denormalized
    icon_url: Optional[str] = None # Denormalized

    earned_at: datetime = Field(default_factory=datetime.utcnow)
    # progress: Optional[List[UserAchievementProgress]] = Field(None, description="Tracks progress for multi-step/multi-criteria achievements. If None, achievement is fully earned based on a single event matching all criteria.")
    # For now, simplifying: if a UserAchievement record exists, it's fully earned.
    # Progress tracking would be a significant addition to the service logic.

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}

# --- API Request/Response Models ---

class AchievementDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=250)
    icon_url: Optional[str] = None
    criteria: List[AchievementCriteria] = Field(..., min_items=1)
    points_reward: int = Field(default=0, ge=0)
    is_active: bool = True

class AchievementDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    icon_url: Optional[str] = None
    criteria: Optional[List[AchievementCriteria]] = Field(None, min_items=1)
    points_reward: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

# Response model for user's achievements could be UserAchievement itself or a summary
class UserAchievementResponse(UserAchievement):
    pass

# --- Loyalty System (Optional - Basic Foundation) ---
class UserLoyalty(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID, typically user_wallet_address")
    user_wallet_address: str = Field(..., index=True)
    current_points: int = Field(default=0, ge=0)
    # loyalty_tier_name: Optional[str] = None # If distinct tiers are defined
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}
