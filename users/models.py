from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    wallet_address: str = Field(..., description="User's unique wallet address", index=True)
    nickname: Optional[str] = Field(None, max_length=50, description="User's optional nickname")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
        # Pydantic v2 config
        model_config = {
            "from_attributes": True, # If data comes from ORM-like objects
            "populate_by_name": True,
            "json_encoders": {
                datetime: lambda dt: dt.isoformat()
            },
            "arbitrary_types_allowed": True # For potential future ObjectId use if schema changes
        }

class UserCreate(BaseModel):
    wallet_address: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="User's optional nickname to update")
