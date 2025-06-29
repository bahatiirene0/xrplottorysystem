from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class PrizeTierConfig(BaseModel):
    tier_name: str = Field(..., description="Name of the prize tier (e.g., 'Jackpot', 'Match 4', 'Second Prize')")
    description: Optional[str] = Field(None, max_length=100, description="Brief description of what this tier rewards")

    # For "Pick N" games, defines how many numbers must match.
    # For "Raffle" games, could indicate rank (e.g., 1 for 1st prize, 2 for 2nd).
    matches_required: Optional[int] = Field(None, ge=0, description="Numbers to match for 'Pick N', or rank for 'Raffle'")

    is_jackpot_tier: bool = Field(False, description="Indicates if this is the main jackpot tier")

    percentage_of_prize_pool: Optional[float] = Field(None, ge=0, le=100, description="Percentage of the total prize pool allocated to this tier (0-100).")
    fixed_prize_amount: Optional[float] = Field(None, gt=0, description="A fixed prize amount for this tier. If set, percentage_of_prize_pool is ignored for this tier.")

    # For progressive jackpots (defined in step 6 of the plan)
    contributes_to_rollover_if_unwon: bool = Field(False, description="If true and this tier is not won, its allocated prize money contributes to the category's rollover.")

    @validator('percentage_of_prize_pool', always=True)
    def check_prize_allocation_logic(cls, v, values):
        if values.get('fixed_prize_amount') is not None and v is not None:
            raise ValueError("Cannot have both fixed_prize_amount and percentage_of_prize_pool for a single tier.")
        if values.get('fixed_prize_amount') is None and v is None:
            raise ValueError("Must have either fixed_prize_amount or percentage_of_prize_pool for a tier.")
        return v


class LotteryCategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Name of the lottery category")
    description: Optional[str] = Field(None, max_length=250, description="Brief description")
    game_type: str = Field(..., description="Type of game (e.g., 'pick_n_digits', 'raffle')") # Added from previous understanding
    game_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration specific to the game_type") # Added

    draw_interval_type: str = Field(..., description="Interval type (e.g., 'minutes', 'daily', 'manual')")
    draw_interval_value: Optional[int] = Field(None, gt=0, description="Value for interval. Not needed if 'manual'.")

    ticket_price: float = Field(..., gt=0, description="Price of a single ticket.") # Assuming this is still relevant even if free-to-play for now
    base_prize_pool: float = Field(default=0.0, ge=0, description="Base prize pool amount for each draw of this category, before any rollovers.")
    winner_fee_percentage: float = Field(default=0.0, ge=0, le=100, description="Percentage of winnings taken as a fee (0-100).")

    prize_tiers: List[PrizeTierConfig] = Field(..., min_items=1, description="Configuration for different prize tiers.")

    is_active: bool = Field(True, description="Whether this category is active.")
    current_rollover_amount: float = Field(default=0.0, ge=0, description="Current accumulated rollover amount for progressive jackpots in this category.")


    @validator('prize_tiers')
    def validate_tier_percentages_and_jackpot(cls, tiers: List[PrizeTierConfig]):
        percentage_sum = sum(t.percentage_of_prize_pool for t in tiers if t.percentage_of_prize_pool is not None and t.fixed_prize_amount is None)
        if percentage_sum > 100.0:
            raise ValueError("Sum of percentage_of_prize_pool for non-fixed tiers cannot exceed 100.")

        jackpot_tiers_count = sum(1 for t in tiers if t.is_jackpot_tier)
        # Allowing multiple jackpot tiers or zero, depending on game design flexibility.
        # For now, no strict validation on count of jackpot_tiers, can be added if needed.
        # if jackpot_tiers_count != 1:
        #     raise ValueError("Exactly one prize tier must be marked as is_jackpot_tier=True.")
        return tiers

class LotteryCategoryCreate(LotteryCategoryBase):
    pass

class LotteryCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    game_type: Optional[str] = None
    game_config: Optional[Dict[str, Any]] = None
    draw_interval_type: Optional[str] = None
    draw_interval_value: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[float] = Field(None, gt=0)
    base_prize_pool: Optional[float] = Field(None, ge=0)
    winner_fee_percentage: Optional[float] = Field(None, ge=0, le=100)
    prize_tiers: Optional[List[PrizeTierConfig]] = Field(None, min_items=1)
    is_active: Optional[bool] = None
    current_rollover_amount: Optional[float] = Field(None, ge=0) # Typically updated by system, but allow manual override


class LotteryCategory(LotteryCategoryBase):
    id: str = Field(alias='_id', description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
        # Pydantic v2 config
        model_config = {
            "from_attributes": True,
            "populate_by_name": True,
            "json_encoders": {
                datetime: lambda dt: dt.isoformat()
            },
            "arbitrary_types_allowed": True # If we use ObjectId directly in future
        }
