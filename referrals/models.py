from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ReferralCodeBase(BaseModel):
    code: str = Field(..., description="The unique referral code string.", index=True) # Mark for indexing
    wallet_address: str = Field(..., description="The wallet address of the user who owns this code.", index=True) # Mark for indexing
    usage_count: int = Field(0, ge=0, description="Number of times this code has been successfully used.")
    is_active: bool = Field(True, description="Whether this referral code is currently active.")

class ReferralCodeCreate(ReferralCodeBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReferralCodeUpdate(BaseModel):
    usage_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReferralCode(ReferralCodeBase):
    id: str = Field(alias='_id', description="MongoDB document ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {
            "from_attributes": True,
            "populate_by_name": True,
            "json_encoders": {datetime: lambda dt: dt.isoformat()},
            "arbitrary_types_allowed": True
        }

class ReferralLinkBase(BaseModel):
    referrer_wallet_address: str = Field(..., description="Wallet address of the user who referred.", index=True)
    referee_wallet_address: str = Field(..., description="Wallet address of the user who was referred.", unique=True, index=True) # Mark as unique and for indexing
    referral_code_used: str = Field(..., description="The referral code that was used for this link.")
    reward_status: str = Field("pending_first_purchase", description="Status of the referral reward (e.g., 'pending_first_purchase', 'eligible_for_reward', 'reward_credited', 'reward_failed').")

class ReferralLinkCreate(ReferralLinkBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReferralLinkUpdate(BaseModel):
    reward_status: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReferralLink(ReferralLinkBase):
    id: str = Field(alias='_id', description="MongoDB document ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {
            "from_attributes": True,
            "populate_by_name": True,
            "json_encoders": {datetime: lambda dt: dt.isoformat()},
            "arbitrary_types_allowed": True
        }

# For API responses, e.g., when getting user's referral stats
class UserReferralStats(BaseModel):
    wallet_address: str
    referral_code: Optional[str] = None # User's own code
    referral_code_usage_count: int = 0
    successful_referrals_count: int = 0 # Number of referees who completed action
    # potential_rewards_pending: int = 0 # Could add more detailed stats
    # total_rewards_earned_summary: str = "N/A" # Summary of rewards
    referred_by: Optional[str] = None # Wallet address of who referred this user, if any

class MyReferralCodeResponse(BaseModel):
    code: str
    usage_count: int
    is_active: bool
    created_at: datetime
    wallet_address: str
    id: str
