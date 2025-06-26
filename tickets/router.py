from fastapi import APIRouter, HTTPException, Depends
from .models import TicketPurchaseRequest, TicketPurchaseResponse, TicketEntry, TicketCreate, PickNSelectionData
from . import db as tickets_db
from draws import db as draws_db
from draws.models import DrawCreate as DrawCreateSchema, DrawUpdate as DrawUpdateSchema, Draw as DrawSchema
from lottery_categories.db import get_category_by_id as get_category_db_by_id
from lottery_categories.models import LotteryCategory
from referrals import db as referrals_db # Import referrals DB functions
from gamification.services import gamification_service # Import gamification service
from gamification.models import AchievementEventType # Import event types
from datetime import datetime
from typing import List, Optional, Any
from pymongo.errors import PyMongoError

router = APIRouter()

def validate_pick_n_selection(selection: List[Any], game_config: dict) -> PickNSelectionData:
    """
    Validates user's selection for a Pick N game against the category's game_config.
    Returns PickNSelectionData if valid, otherwise raises HTTPException.
    """
    num_picks_expected = game_config.get('num_picks')
    min_val = game_config.get('min_digit') # Assuming digits for now
    max_val = game_config.get('max_digit') # Assuming digits for now
    allow_duplicates = game_config.get('allow_duplicates', False)

    if not isinstance(num_picks_expected, int) or \
       not isinstance(min_val, int) or \
       not isinstance(max_val, int):
        raise HTTPException(status_code=500, detail="Invalid game_config for Pick N category.")

    if len(selection) != num_picks_expected:
        raise HTTPException(status_code=400, detail=f"Invalid selection: Expected {num_picks_expected} picks, got {len(selection)}.")

    if not allow_duplicates and len(set(selection)) != len(selection):
        raise HTTPException(status_code=400, detail="Invalid selection: Duplicate picks are not allowed.")

    for pick in selection:
        try:
            pick_val = int(pick) # Assuming picks are convertible to int for digit games
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid selection: Pick '{pick}' is not a valid number.")
        if not (min_val <= pick_val <= max_val):
            raise HTTPException(status_code=400, detail=f"Invalid selection: Pick '{pick_val}' is out of range ({min_val}-{max_val}).")

    return PickNSelectionData(picks=selection)


@router.post("/buy", response_model=TicketPurchaseResponse)
def buy_tickets(req: TicketPurchaseRequest):
    if req.num_tickets < 1:
        raise HTTPException(status_code=400, detail="Must buy at least one ticket.")

    active_draw_id: str
    ticket_selection_data: Optional[PickNSelectionData] = None

    try:
        category: Optional[LotteryCategory] = get_category_db_by_id(req.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Lottery category {req.category_id} not found.")
        if not category.is_active:
            raise HTTPException(status_code=400, detail=f"Lottery category {req.category_id} is not active.")

        # Handle game-specific selection
        if category.game_type == "pick_n_digits": # Or other "pick_n_..." types
            if req.selection is None:
                raise HTTPException(status_code=400, detail=f"Selection is required for game type '{category.game_type}'.")
            ticket_selection_data = validate_pick_n_selection(req.selection, category.game_config)
        elif req.selection is not None:
            # If selection is provided for a non-pick_n game (e.g., raffle)
            raise HTTPException(status_code=400, detail=f"Selection data is not applicable for game type '{category.game_type}'.")

        # Find or create an open draw (existing logic from previous step)
        open_draws = draws_db.get_open_draws_for_category(req.category_id)
        target_draw: Optional[DrawSchema] = None
        if open_draws:
            target_draw = open_draws[0]

        if not target_draw:
            now = datetime.utcnow()
            next_pending = draws_db.get_next_pending_draw(req.category_id)
            if next_pending and next_pending.scheduled_open_time <= now:
                update_res = draws_db.update_draw(next_pending.id, DrawUpdateSchema(status="open", actual_open_time=now))
                if update_res:
                    target_draw = draws_db.get_draw_by_id(next_pending.id)
                else:
                    raise HTTPException(status_code=500, detail="Failed to open a pending draw for ticket purchase.")

            if not target_draw:
                if category.draw_interval_type == "manual":
                     raise HTTPException(status_code=400, detail=f"Category {category.name} is manual. No open draw available and new draws must be created manually.")
                try:
                    new_draw_payload = DrawCreateSchema.from_category(category, start_time=now)
                    new_draw_payload.status = "open"
                    created_draw_id = draws_db.create_draw(new_draw_payload)
                    if not created_draw_id:
                        raise HTTPException(status_code=500, detail="Failed to create a new draw for ticket purchase.")
                    draws_db.update_draw(created_draw_id, DrawUpdateSchema(actual_open_time=now))
                    target_draw = draws_db.get_draw_by_id(created_draw_id)
                except ValueError as ve:
                    raise HTTPException(status_code=400, detail=f"Cannot create draw: {str(ve)}")

        if not target_draw or target_draw.id is None:
            raise HTTPException(status_code=500, detail="Could not find or create an active draw for the category.")
        if target_draw.status != "open":
             raise HTTPException(status_code=400, detail=f"The current draw {target_draw.id} for category {category.name} is not open. Status: {target_draw.status}")
        active_draw_id = target_draw.id

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error preparing for ticket purchase: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error preparing for ticket purchase: {str(e)}")

    # Process referral code before ticket purchase loop
    # but after validating category and finding/creating a draw,
    # to ensure the core purchase intent is valid first.
    applied_referral_code_owner: Optional[str] = None
    is_newly_referred_user = False

    if req.referral_code:
        try:
            ref_code_obj = referrals_db.get_referral_code_by_code(req.referral_code)
            if not ref_code_obj or not ref_code_obj.is_active:
                # Optionally, inform user about invalid code, or silently ignore. For now, ignore.
                print(f"Referral code {req.referral_code} is invalid or inactive.")
            elif ref_code_obj.wallet_address == req.wallet_address:
                print(f"User {req.wallet_address} attempted self-referral with code {req.referral_code}.")
            else:
                # Check if this user (referee) has already been linked/referred
                existing_link = referrals_db.get_referral_link_by_referee(req.wallet_address)
                if not existing_link:
                    # New referee, create the link
                    new_link = referrals_db.create_referral_link(
                        referrer_wallet=ref_code_obj.wallet_address,
                        referee_wallet=req.wallet_address,
                        referral_code_used=req.referral_code
                    )
                    if new_link:
                        print(f"Referral link created: {new_link.id} for referee {req.wallet_address} by {ref_code_obj.wallet_address}")
                        referrals_db.increment_referral_code_usage(ref_code_obj.id) # Use code's MongoDB ID
                        applied_referral_code_owner = ref_code_obj.wallet_address
                        is_newly_referred_user = True # Mark for potential reward trigger post-purchase
                    else:
                        print(f"Failed to create referral link for {req.wallet_address} using code {req.referral_code}")
                else:
                    print(f"User {req.wallet_address} has already been referred by {existing_link.referrer_wallet_address} using code {existing_link.referral_code_used}.")

        except PyMongoError as e:
            print(f"PyMongoError during referral processing for code {req.referral_code}: {e}")
            # Non-critical error for referral, proceed with ticket purchase if desired.
        except Exception as e:
            print(f"Unexpected error during referral processing for code {req.referral_code}: {e}")


    purchased_ticket_ids = []
    for _ in range(req.num_tickets):
        ticket_to_create = TicketCreate(
            wallet_address=req.wallet_address,
            draw_id=active_draw_id,
            timestamp=datetime.utcnow(),
            selection_data=ticket_selection_data
        )
        try:
            ticket_id = tickets_db.create_ticket(ticket_to_create)
            if ticket_id:
                purchased_ticket_ids.append(ticket_id)
            else:
                raise HTTPException(status_code=500, detail="Failed to save one or more tickets to database.")
        except PyMongoError as e:
            raise HTTPException(status_code=500, detail=f"Database error while saving a ticket: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error while saving a ticket: {str(e)}")

    if not purchased_ticket_ids or len(purchased_ticket_ids) != req.num_tickets:
        raise HTTPException(status_code=500, detail="Could not purchase all requested tickets. Partial transaction may have occurred.")

    # --- Gamification Event: Ticket Purchase ---
    try:
        # Assuming category is fetched and available
        event_data_ticket_purchase = {
            "count": len(purchased_ticket_ids),
            "category_id": req.category_id,
            # "total_value": category.ticket_price * len(purchased_ticket_ids) # If needed by an achievement
        }
        gamification_service.process_event(
            user_wallet_address=req.wallet_address,
            event_type=AchievementEventType.TICKET_PURCHASE,
            event_data=event_data_ticket_purchase
        )
    except Exception as e_gami:
        # Log gamification processing error but don't let it fail the main transaction
        print(f"Error processing gamification event for ticket purchase: {e_gami}")
    # --- End Gamification Event ---


    # After successful ticket purchase, if the user was newly referred, update their referral link status
    if is_newly_referred_user and applied_referral_code_owner: # Sanity check
        try:
            link_to_update = referrals_db.get_referral_link_by_referee(req.wallet_address)
            if link_to_update and link_to_update.reward_status == "pending_first_purchase":
                updated = referrals_db.update_referral_link_status(link_to_update.id, "eligible_for_reward")
                if updated:
                    print(f"Referral link {link_to_update.id} for referee {req.wallet_address} (referred by {link_to_update.referrer_wallet_address}) status updated to 'eligible_for_reward'. Reward due to referrer.")

                    # --- Gamification Event: Referral Success ---
                    try:
                        event_data_referral = {"count": 1} # For one successful referral
                        gamification_service.process_event(
                            user_wallet_address=link_to_update.referrer_wallet_address, # Event for the referrer
                            event_type=AchievementEventType.REFERRAL_SUCCESS,
                            event_data=event_data_referral
                        )
                    except Exception as e_gami_ref:
                        print(f"Error processing gamification event for referral success: {e_gami_ref}")
                    # --- End Gamification Event ---
                else:
                    print(f"Failed to update referral link status for {link_to_update.id} after purchase.")
        except PyMongoError as e:
            print(f"PyMongoError updating referral link status for {req.wallet_address} post-purchase: {e}")
        except Exception as e: # Catch any other unexpected error
            print(f"Unexpected error updating referral link status for {req.wallet_address} post-purchase: {e}")


    return TicketPurchaseResponse(
        success=True,
        message=f"{len(purchased_ticket_ids)} tickets purchased successfully for category {req.category_id}, draw {active_draw_id}.",
        tickets=purchased_ticket_ids
    )

@router.get("/list/{wallet_address}", response_model=List[TicketEntry])
def list_tickets(wallet_address: str):
    try:
        tickets = tickets_db.get_tickets_by_wallet(wallet_address)
        return tickets
    except PyMongoError as e:
        print(f"PyMongoError listing tickets: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the database while listing tickets.")
    except Exception as e:
        print(f"Unexpected error listing tickets: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while listing tickets.")

@router.get("/{ticket_id}", response_model=TicketEntry)
def get_ticket(ticket_id: str):
    try:
        ticket = tickets_db.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        return ticket
    except PyMongoError as e:
        print(f"PyMongoError getting ticket by ID: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the database while retrieving the ticket.")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e: # Catch all other exceptions, like invalid ObjectId format if not handled in db layer
        print(f"Unexpected error getting ticket by ID: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred or ticket ID format is invalid.")
