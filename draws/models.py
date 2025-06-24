from pydantic import BaseModel, Field
from typing import List, Optional
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
    ledger_hash: Optional[str] = None
    winner: Optional[str] = None

    # General timestamp for record creation, can be different from open/close times
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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

        return cls(
            category_id=category.id,
            scheduled_open_time=open_time,
            scheduled_close_time=close_time,
            status="pending_open" # Draws are pending until their open time
        )


# Model for updating a draw
class DrawUpdate(BaseModel):
    status: Optional[str] = None
    actual_open_time: Optional[datetime] = None
    actual_close_time: Optional[datetime] = None
    participants: Optional[List[str]] = None # Usually updated systemically
    ledger_hash: Optional[str] = None
    winner: Optional[str] = None
    # category_id, scheduled times are generally not updated after creation.
    # updated_at will be set in DB layer
