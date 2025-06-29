from fastapi import APIRouter, HTTPException, Depends, Body, Path, Query
from typing import List, Optional

from . import db as syndicate_db
from .models import (
    Syndicate, SyndicateCreateRequest, SyndicateUpdateRequest, SyndicateResponse,
    InviteMemberRequest, SyndicateMemberStatus, SyndicateParticipateRequest,
    SyndicateTicketPurchase, SyndicateSummaryResponse
)
from users.db import get_user_by_wallet_address # For checking if invited user exists, getting nickname
from tickets.router import buy_tickets # To "buy" tickets for the syndicate
from tickets.models import TicketPurchaseRequest # For the above
from draws.db import get_draw_by_id # To validate draw for participation
from auth.dependencies import get_current_user_from_token
from auth.models import TokenData
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Syndicate Management ---

@router.post("/", response_model=SyndicateResponse, status_code=201, summary="Create a new syndicate")
async def create_new_syndicate(
    request_data: SyndicateCreateRequest,
    token_data: TokenData = Depends(get_current_user_from_token)
):
    creator_wallet = token_data.wallet_address
    syndicate = syndicate_db.create_syndicate(
        name=request_data.name,
        description=request_data.description,
        creator_wallet_address=creator_wallet,
        default_category_id=request_data.default_lottery_category_id
    )
    if not syndicate:
        raise HTTPException(status_code=500, detail="Failed to create syndicate.")
    return syndicate

@router.get("/my_syndicates", response_model=List[SyndicateSummaryResponse], summary="List syndicates for the current user")
async def list_my_syndicates(token_data: TokenData = Depends(get_current_user_from_token)):
    user_wallet = token_data.wallet_address
    syndicates = syndicate_db.get_syndicates_for_member(user_wallet)
    # Convert full Syndicate objects to SyndicateSummaryResponse
    summaries = []
    for synd in syndicates:
        if synd.id: # Ensure id is present
            summaries.append(SyndicateSummaryResponse(
                id=synd.id,
                name=synd.name,
                creator_wallet_address=synd.creator_wallet_address,
                member_count=len([m for m in synd.members if m.status == SyndicateMemberStatus.ACTIVE]),
                created_at=synd.created_at
            ))
    return summaries


@router.get("/{syndicate_id}", response_model=SyndicateResponse, summary="Get syndicate details")
async def get_syndicate_details(
    syndicate_id: str = Path(..., description="ID of the syndicate to retrieve"),
    token_data: TokenData = Depends(get_current_user_from_token) # User must be member to view? Or public? For now, authenticated.
):
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    # Optional: Check if current user is a member before returning details
    # current_user_wallet = token_data.wallet_address
    # if not any(member.wallet_address == current_user_wallet and member.status == SyndicateMemberStatus.ACTIVE for member in syndicate.members):
    #     if syndicate.creator_wallet_address != current_user_wallet : # allow creator
    #          raise HTTPException(status_code=403, detail="Not authorized to view this syndicate's details.")
    return syndicate

@router.put("/{syndicate_id}", response_model=SyndicateResponse, summary="Update syndicate details (admin only)")
async def update_syndicate_info(
    syndicate_id: str = Path(..., description="ID of the syndicate to update"),
    request_data: SyndicateUpdateRequest = Body(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if syndicate.creator_wallet_address != current_user_wallet:
        raise HTTPException(status_code=403, detail="Only the syndicate creator can update its details.")

    updated_syndicate = syndicate_db.update_syndicate_details(
        syndicate_id=syndicate_id,
        name=request_data.name,
        description=request_data.description,
        default_category_id=request_data.default_lottery_category_id
    )
    if not updated_syndicate:
        # This could be due to no actual changes or a DB error not caught by get_syndicate_by_id after update
        current_data = syndicate_db.get_syndicate_by_id(syndicate_id) # Re-fetch
        if current_data and \
           (current_data.name == request_data.name or request_data.name is None) and \
           (current_data.description == request_data.description or request_data.description is None) and \
           (current_data.default_lottery_category_id == request_data.default_lottery_category_id or request_data.default_lottery_category_id is None) :
             return current_data # No change was made, return current
        raise HTTPException(status_code=500, detail="Failed to update syndicate details.")
    return updated_syndicate

@router.delete("/{syndicate_id}", status_code=204, summary="Delete a syndicate (admin only)")
async def delete_syndicate(
    syndicate_id: str = Path(..., description="ID of the syndicate to delete"),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if syndicate.creator_wallet_address != current_user_wallet:
        raise HTTPException(status_code=403, detail="Only the syndicate creator can delete the syndicate.")

    # Consider further checks: e.g., cannot delete if syndicate has pending winnings or active draw participations.
    # For now, direct deletion.
    if not syndicate_db.delete_syndicate_by_id(syndicate_id):
        raise HTTPException(status_code=500, detail="Failed to delete syndicate.")
    return None # No content

# --- Syndicate Member Management ---

@router.post("/{syndicate_id}/members/invite", response_model=SyndicateResponse, summary="Invite a user to join a syndicate (admin only)")
async def invite_syndicate_member(
    syndicate_id: str = Path(...),
    request_data: InviteMemberRequest = Body(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if syndicate.creator_wallet_address != current_user_wallet:
        raise HTTPException(status_code=403, detail="Only syndicate creator can invite members.")

    invited_wallet = request_data.member_wallet_address
    if not get_user_by_wallet_address(invited_wallet): # Check if invited user exists in our system
        raise HTTPException(status_code=404, detail=f"User with wallet {invited_wallet} not found in the system.")

    if any(member.wallet_address == invited_wallet for member in syndicate.members if member.status != SyndicateMemberStatus.LEFT and member.status != SyndicateMemberStatus.REMOVED):
        raise HTTPException(status_code=400, detail=f"User {invited_wallet} is already a member or has a pending invite.")

    updated_syndicate = syndicate_db.add_or_update_syndicate_member(
        syndicate_id, invited_wallet, SyndicateMemberStatus.INVITED, invited_by_wallet=current_user_wallet
    )
    if not updated_syndicate:
        raise HTTPException(status_code=500, detail="Failed to invite member.")
    return updated_syndicate

@router.post("/{syndicate_id}/members/accept_invite", response_model=SyndicateResponse, summary="Accept an invitation to join a syndicate")
async def accept_syndicate_invite(
    syndicate_id: str = Path(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")

    member_to_activate = next((m for m in syndicate.members if m.wallet_address == current_user_wallet and m.status == SyndicateMemberStatus.INVITED), None)
    if not member_to_activate:
        raise HTTPException(status_code=400, detail="No pending invitation found for this user in this syndicate, or user already active.")

    updated_syndicate = syndicate_db.add_or_update_syndicate_member(
        syndicate_id, current_user_wallet, SyndicateMemberStatus.ACTIVE
    )
    if not updated_syndicate:
        raise HTTPException(status_code=500, detail="Failed to accept invitation.")
    return updated_syndicate

@router.post("/{syndicate_id}/members/leave", response_model=SyndicateResponse, summary="Leave a syndicate")
async def leave_syndicate(
    syndicate_id: str = Path(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if not any(m.wallet_address == current_user_wallet and m.status == SyndicateMemberStatus.ACTIVE for m in syndicate.members):
        raise HTTPException(status_code=400, detail="User is not an active member of this syndicate.")
    if syndicate.creator_wallet_address == current_user_wallet and len([m for m in syndicate.members if m.status == SyndicateMemberStatus.ACTIVE]) > 1:
        raise HTTPException(status_code=400, detail="Creator cannot leave the syndicate if other active members exist. Transfer ownership or remove members first.")

    updated_syndicate = syndicate_db.remove_syndicate_member(syndicate_id, current_user_wallet, new_status=SyndicateMemberStatus.LEFT)
    if not updated_syndicate:
        raise HTTPException(status_code=500, detail="Failed to leave syndicate.")
    # If creator leaves and is the last member, the syndicate could be auto-deleted or marked inactive.
    # For now, just marks as LEFT. If creator leaves as last member, they can then delete it.
    return updated_syndicate

@router.delete("/{syndicate_id}/members/{member_wallet_address}", response_model=SyndicateResponse, summary="Remove a member from a syndicate (admin only)")
async def remove_member_from_syndicate(
    syndicate_id: str = Path(...),
    member_wallet_address: str = Path(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if syndicate.creator_wallet_address != current_user_wallet:
        raise HTTPException(status_code=403, detail="Only syndicate creator can remove members.")
    if member_wallet_address == current_user_wallet:
        raise HTTPException(status_code=400, detail="Creator cannot remove themselves using this endpoint. Use 'leave' or 'delete syndicate'.")

    member_exists = any(m.wallet_address == member_wallet_address and (m.status == SyndicateMemberStatus.ACTIVE or m.status == SyndicateMemberStatus.INVITED) for m in syndicate.members)
    if not member_exists:
        raise HTTPException(status_code=404, detail=f"Member {member_wallet_address} not found or not in a removable state in this syndicate.")

    updated_syndicate = syndicate_db.remove_syndicate_member(syndicate_id, member_wallet_address, new_status=SyndicateMemberStatus.REMOVED)
    if not updated_syndicate:
        raise HTTPException(status_code=500, detail=f"Failed to remove member {member_wallet_address}.")
    return updated_syndicate

# --- Syndicate Draw Participation ---
@router.post("/{syndicate_id}/draws/{draw_id}/participate", response_model=SyndicateTicketPurchase, summary="Purchase tickets for a syndicate for a specific draw (admin only)")
async def syndicate_participate_in_draw(
    syndicate_id: str = Path(...),
    draw_id: str = Path(...),
    request_data: SyndicateParticipateRequest = Body(...),
    token_data: TokenData = Depends(get_current_user_from_token)
):
    current_user_wallet = token_data.wallet_address
    syndicate = syndicate_db.get_syndicate_by_id(syndicate_id)
    if not syndicate:
        raise HTTPException(status_code=404, detail="Syndicate not found.")
    if syndicate.creator_wallet_address != current_user_wallet: # Only admin can initiate participation
        raise HTTPException(status_code=403, detail="Only syndicate admin can purchase tickets for the syndicate.")

    draw = get_draw_by_id(draw_id)
    if not draw:
        raise HTTPException(status_code=404, detail=f"Draw {draw_id} not found.")
    if draw.status != "open":
        raise HTTPException(status_code=400, detail=f"Draw {draw_id} is not open for ticket purchase. Status: {draw.status}")

    # For "Pick N" games, selection data would be needed.
    # This endpoint simplifies by assuming the admin (current_user_wallet) "buys" tickets.
    # These tickets are regular tickets but their IDs are logged under SyndicateTicketPurchase.
    # The actual "cost" is conceptual in a free-to-play model.

    # Get category for selection validation if needed
    # from lottery_categories.db import get_category_by_id as get_lottery_category
    # category = get_lottery_category(draw.category_id)
    # if not category:
    #     raise HTTPException(status_code=500, detail="Failed to load category for draw.")
    # if category.game_type == "pick_n_digits" and not request_data.selections:
    #     raise HTTPException(status_code=400, detail="Selections are required for Pick N Digit games.")
    # TODO: Handle selections if game_type is pick_n_digits. For now, assume raffle or admin handles selection via other means.

    purchased_ticket_ids: List[str] = []
    try:
        # The buy_tickets function from tickets.router is a FastAPI endpoint function.
        # It's not ideal to call it directly. We should use the underlying DB operations or a service layer.
        # For now, let's simulate what it does: create ticket entries.
        # This part needs careful refactoring if buy_tickets has complex logic we need to replicate.
        # A better way: Ticket creation logic should be in a service/DB function callable from both routers.

        # Simplified direct ticket creation (attributes to syndicate admin for now)
        from tickets.db import create_ticket as create_ticket_db
        from tickets.models import TicketCreate #, PickNSelectionData

        for i in range(request_data.num_tickets):
            # If PickN, would need selection data here.
            # selection_data_for_ticket = PickNSelectionData(picks=request_data.selections[i]) if request_data.selections else None
            ticket_to_create = TicketCreate(
                wallet_address=current_user_wallet, # Ticket is "owned" by syndicate admin
                draw_id=draw_id,
                # selection_data=selection_data_for_ticket
            )
            ticket_id = create_ticket_db(ticket_to_create)
            if not ticket_id:
                raise HTTPException(status_code=500, detail=f"Failed to create one or more tickets for syndicate (ticket {i+1}).")
            purchased_ticket_ids.append(ticket_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tickets for syndicate participation: {e}")
        raise HTTPException(status_code=500, detail="Error processing syndicate ticket purchase.")

    if not purchased_ticket_ids:
        raise HTTPException(status_code=500, detail="No tickets were purchased for the syndicate.")

    syndicate_purchase_record = syndicate_db.record_syndicate_ticket_purchase(
        syndicate_id=syndicate_id,
        draw_id=draw_id,
        purchased_by_wallet=current_user_wallet,
        ticket_ids=purchased_ticket_ids
    )
    if not syndicate_purchase_record:
        # This is problematic: tickets were created but not logged for syndicate.
        # Ideally, ticket creation and logging should be atomic or have rollback.
        logger.error(f"Tickets {purchased_ticket_ids} created for syndicate {syndicate_id} but failed to record syndicate purchase log.")
        raise HTTPException(status_code=500, detail="Failed to log syndicate ticket purchase after tickets were created.")

    return syndicate_purchase_record

# Need to add this router to app.py:
# from syndicates.router import router as syndicates_router
# app.include_router(syndicates_router, prefix="/api/syndicates", tags=["Syndicates"])
