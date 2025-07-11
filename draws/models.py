from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any # Added Dict, Any
from datetime import datetime, timedelta

# Represents a Draw document in MongoDB
class Draw(BaseModel):
    id: Optional[str] = Field(alias='_id', default=None) # MongoDB ID
    category_id: str = Field(..., description="ID of the LotteryCategory this draw belongs to")
    status: str  # e.g., "pending_open", "open", "closed", "completed", "cancelled"

    scheduled_open_time: datetime = Field(..., description="Time when this draw is scheduled to open for ticket sales")
    scheduled_close_time: datetime = Field(..., description="Time when this draw is scheduled to close for ticket sales")
    actual_open_time: Optional[datetime] = Field(None, description="Actual time draw opened (if different from scheduled)")
    actual_close_time: Optional[datetime] = Field(None, description="Actual time draw closed (if different from scheduled)")

    participants: List[str] = Field(default_factory=list, description="List of wallet addresses of participants")
    ledger_hash: Optional[str] = None # Used for raffle winner selection, and as seed for PickN winning numbers

    # For Pick N games: stores the generated winning numbers/symbols
    winning_selection: Optional[Dict[str, Any]] = Field(None, description="Drawn winning numbers/symbols, e.g., {'picks': [1,2,3]}")

    # Replaces single 'winner' to support tiers and multiple winners
    winners_by_tier: Optional[List['PrizeTierWinner']] = Field(default_factory=list, description="List of winners categorized by prize tier")

    # General timestamp for record creation, can be different from open/close times
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Prize pool for this specific draw instance
    base_prize_pool: float = Field(default=0.0, ge=0, description="The base prize pool amount for this specific draw instance (category base + category rollover at time of creation).")


    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
        model_config = {
            "from_attributes": True,
            "populate_by_name": True,
             "json_encoders": {
                datetime: lambda dt: dt.isoformat()
            },
            "arbitrary_types_allowed": True
        }

# Model for creating a new draw
class DrawCreate(BaseModel):
    category_id: str
    status: str = "pending_open" # Default status for a newly created scheduled draw
    scheduled_open_time: datetime
    scheduled_close_time: datetime
    base_prize_pool: Optional[float] = Field(None, ge=0, description="Initial prize pool for this draw. If None, will be derived from category during creation.")
    # created_at and updated_at will be set in DB layer

    @classmethod
    def from_category(cls, category: 'lottery_categories.models.LotteryCategory', start_time: Optional[datetime] = None):
        """
        Helper to create DrawCreate payload based on a category's interval.
        If start_time is None, it's scheduled to start 'now' (or slightly in future).
        This is a utility, actual scheduling logic might be more complex.
        """
        if start_time is None:
            # Add a small buffer to ensure open_time is not in the past if processing takes time
            start_time = datetime.utcnow() + timedelta(seconds=5)

        open_time = start_time
        close_time: datetime

        if category.draw_interval_type == "minutes":
            close_time = open_time + timedelta(minutes=category.draw_interval_value or 0)
        elif category.draw_interval_type == "hourly":
            close_time = open_time + timedelta(hours=category.draw_interval_value or 0)
        elif category.draw_interval_type == "daily":
            close_time = open_time + timedelta(days=category.draw_interval_value or 0)
        elif category.draw_interval_type == "weekly":
            close_time = open_time + timedelta(weeks=category.draw_interval_value or 0)
        elif category.draw_interval_type == "manual":
            # For manual, close_time might need to be set explicitly or much later
            # This example sets it arbitrarily far; adjust as needed.
            close_time = open_time + timedelta(days=365) # Default for manual, should be overridden
        else:
            raise ValueError(f"Unsupported draw_interval_type: {category.draw_interval_type}")

        # Calculate the initial prize pool for this draw instance
        # It's the category's base pool plus any current rollover amount from the category.
        initial_draw_prize_pool = category.base_prize_pool + category.current_rollover_amount

        return cls(
            category_id=category.id,
            scheduled_open_time=open_time,
            scheduled_close_time=close_time,
            status="pending_open", # Draws are pending until their open time
            base_prize_pool=initial_draw_prize_pool
        )


# Model for updating a draw
class DrawUpdate(BaseModel):
    status: Optional[str] = None
    actual_open_time: Optional[datetime] = None
    actual_close_time: Optional[datetime] = None
    participants: Optional[List[str]] = None # Usually updated systemically
    ledger_hash: Optional[str] = None # Still set for raffles, and as seed for PickN
    winning_selection: Optional[Dict[str, Any]] = None # For PickN games
    winners_by_tier: Optional[List['PrizeTierWinner']] = None # For all game types supporting tiers
    # category_id, scheduled times are generally not updated after creation.
    # updated_at will be set in DB layer

# Define PrizeTierWinner model here so Draw can reference it.
class PrizeTierWinner(BaseModel):
    tier_name: str = Field(..., description="Name of the prize tier, matches PrizeTierConfig.tier_name from LotteryCategory")
    wallet_address: str = Field(..., description="Wallet address of the winner for this tier")
    ticket_id: str = Field(..., description="The specific winning ticket ID for this prize")

    prize_amount_calculated: float = Field(..., ge=0, description="The gross prize amount calculated for this winner for this tier.")
    is_fixed_prize: bool = Field(..., description="Indicates if this prize was a fixed amount or percentage-based.")

    # Fields for fee calculation (added in step 5 of the plan)
    fee_amount_charged: Optional[float] = Field(None, ge=0, description="The amount of fee charged on this winning.")
    net_prize_payable: Optional[float] = Field(None, ge=0, description="The net prize amount payable to the winner after fees.")

    syndicate_win_details: Optional[Dict[str, Any]] = Field(None, description="Details if this win was by a syndicate (e.g., syndicate_id, name, members_count)")
    # selection_matched: Optional[Any] = Field(None, description="What part of their selection matched, if applicable (e.g., for Pick N games)")


# Need to update Draw's model_config if forward refs are used and not automatically handled by Pydantic v2
# For Pydantic v2, forward references (like 'PrizeTierWinner' as a string) are typically handled automatically.
# If using Pydantic v1, might need: Draw.update_forward_refs() after all models are defined.
# For now, assuming Pydantic v2 handles it. If import error or validation error, will address.
