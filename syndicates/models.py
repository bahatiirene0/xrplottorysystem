from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SyndicateMemberStatus(str, Enum):
    INVITED = "invited"
    ACTIVE = "active"
    LEFT = "left"
    REMOVED = "removed"

class SyndicateMember(BaseModel):
    wallet_address: str = Field(..., description="Wallet address of the member")
    nickname: Optional[str] = Field(None, description="Nickname of the member, fetched from User profile if available") # Denormalized for convenience
    join_date: Optional[datetime] = Field(None, description="Timestamp when the member became active")
    status: SyndicateMemberStatus = Field(default=SyndicateMemberStatus.INVITED)
    # share_percentage: Optional[float] = Field(None, ge=0, le=100, description="Individual share percentage, if not equal among active members") # For more complex sharing

class Syndicate(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID")
    name: str = Field(..., min_length=3, max_length=50, description="Name of the syndicate")
    description: Optional[str] = Field(None, max_length=250, description="Optional description for the syndicate")
    creator_wallet_address: str = Field(..., description="Wallet address of the user who created the syndicate (admin)")

    members: List[SyndicateMember] = Field(default_factory=list, description="List of members in the syndicate")

    # Conceptual: Even if free-to-play, this defines how shares are split if not explicitly defined per member.
    # For now, assume equal share among active members.
    # contribution_per_member_per_draw: Optional[float] = Field(None, ge=0, description="Conceptual contribution amount per member for a draw")

    default_lottery_category_id: Optional[str] = Field(None, description="Optional default lottery category this syndicate plays")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}


class SyndicateTicketPurchase(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID")
    syndicate_id: str = Field(..., description="ID of the syndicate that purchased the tickets")
    draw_id: str = Field(..., description="ID of the draw for which tickets were purchased")
    purchased_by_wallet_address: str = Field(..., description="Wallet address of the member (admin) who initiated the purchase")
    ticket_ids: List[str] = Field(..., description="List of actual ticket IDs (from tickets collection) purchased by the syndicate")
    purchase_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}


class MemberShare(BaseModel):
    wallet_address: str
    nickname: Optional[str] = None # Denormalized
    share_of_winnings: float = Field(..., ge=0, description="Amount of winnings allocated to this member")

class SyndicateWinningsDistribution(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id', description="MongoDB document ID")
    syndicate_id: str = Field(..., description="ID of the syndicate")
    draw_id: str = Field(..., description="ID of the draw that was won")
    winning_ticket_id: str = Field(..., description="The specific ticket ID that won")
    total_syndicate_prize_gross: float = Field(..., ge=0, description="Total prize amount won by the syndicate (before platform fees)")
    platform_fee_charged: float = Field(..., ge=0, description="Platform fee deducted from the syndicate's winnings")
    total_syndicate_prize_net: float = Field(..., ge=0, description="Net prize amount for the syndicate after platform fees")
    member_distributions: List[MemberShare] = Field(..., description="Breakdown of winnings distributed to each active member")
    distribution_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True, "populate_by_name": True, "json_encoders": {datetime: lambda dt: dt.isoformat()}}

# --- Request/Response Models for API ---

class SyndicateCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    default_lottery_category_id: Optional[str] = None

class SyndicateUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    default_lottery_category_id: Optional[str] = None

class SyndicateResponse(Syndicate): # Inherits all fields from Syndicate
    pass

class InviteMemberRequest(BaseModel):
    member_wallet_address: str = Field(..., description="Wallet address of the user to invite")

class SyndicateParticipateRequest(BaseModel):
    num_tickets: int = Field(..., gt=0, description="Number of tickets the syndicate wants to 'purchase' for the draw")
    # Selections might be needed if the syndicate plays a "Pick N" game
    # For now, assume raffle or admin picks numbers manually if needed for PickN, then enters them via normal ticket purchase.
    # This endpoint would just log the intent and associate tickets.
    # A simpler model: admin buys tickets normally, then assigns them to syndicate for a draw.
    # For this plan: this endpoint will create new ticket entries attributed to the syndicate admin.

# Response for listing syndicates (could be a simplified version)
class SyndicateSummaryResponse(BaseModel):
    id: str
    name: str
    creator_wallet_address: str
    member_count: int
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        model_config = {"from_attributes": True}
