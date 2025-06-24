from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LotteryCategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Name of the lottery category (e.g., 'Quick 5 Minute Draw', 'Daily Jackpot')")
    description: Optional[str] = Field(None, max_length=250, description="Brief description of the lottery category")
    draw_interval_type: str = Field(..., description="Type of interval (e.g., 'minutes', 'hourly', 'daily', 'weekly', 'manual')")
    draw_interval_value: Optional[int] = Field(None, gt=0, description="Value for the interval (e.g., 5 for 'minutes', 1 for 'daily'). Not needed if 'manual'.")
    ticket_price: float = Field(..., gt=0, description="Price of a single ticket for this lottery category")
    prize_info: Dict[str, Any] = Field(default_factory=dict, description="Details about prizes (e.g., {'first_place': '70% of pool', 'second_place': '20% of pool'})")
    is_active: bool = Field(True, description="Whether this lottery category is currently active and can have new draws")

class LotteryCategoryCreate(LotteryCategoryBase):
    pass

class LotteryCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    draw_interval_type: Optional[str] = None
    draw_interval_value: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[float] = Field(None, gt=0)
    prize_info: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

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
