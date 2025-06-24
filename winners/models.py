from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RecentWinnerInfo(BaseModel):
    draw_id: str
    category_id: str
    category_name: str # Denormalized for convenience
    winning_wallet_address_anonymized: str
    prize_info_summary: Optional[str] = None # e.g., "Jackpot" or a summary from Draw/Category prize_info
    closed_time: datetime # actual_close_time of the draw

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
        # Pydantic v2 config
        model_config = {
            "from_attributes": True, # If data comes from ORM-like objects
             "json_encoders": {
                datetime: lambda dt: dt.isoformat()
            }
        }
