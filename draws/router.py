from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import Draw, DrawCreate, DrawUpdate
from tickets.db import get_tickets_collection as get_ticket_db_collection
from rng.utils import calculate_winner_index
from datetime import datetime
from xrpl.clients import JsonRpcClient
from xrpl.models.requests.ledger import Ledger
from xrpl.clients.exceptions import XRPLClientException
import os

from . import db as draws_db
from lottery_categories.db import get_category_by_id as get_category_db_by_id
from lottery_categories.models import LotteryCategory
from pymongo.errors import PyMongoError

router = APIRouter()

XRPL_RPC_URL = os.environ.get('XRPL_RPC_URL', 'https://s.altnet.rippletest.net:51234/')

# (get_latest_ledger_hash_sync remains the same, so not repeated for brevity)
def get_latest_ledger_hash_sync():
    try:
        client = JsonRpcClient(XRPL_RPC_URL)
        ledger_request = Ledger(ledger_index="validated", transactions=False, expand=False)
        response = client.request(ledger_request)
        result = response.result
        if not response.is_successful() or "ledger_hash" not in result:
            error_message = result.get("error_message") or result.get("error") or "Unknown XRPL error"
            print(f"XRPL request not successful or ledger_hash missing. Response: {result}")
            raise XRPLClientException(f"Failed to get ledger_hash: {error_message}")
        return result.get('ledger_hash')
    except XRPLClientException as e:
        print(f"XRPLClientException in get_latest_ledger_hash_sync: {e}")
        raise
    except Exception as e:
        print(f"Generic Exception in get_latest_ledger_hash_sync: {e}")
        raise XRPLClientException(f"An unexpected error occurred while fetching ledger hash: {e}")


# This endpoint is to manually trigger opening of due "pending_open" draws.
# In a full system, a background scheduler would do this.
@router.post("/process_pending_draws", summary="Manually trigger processing of pending draws to open them if due.")
def process_pending_draws_endpoint(category_id: Optional[str] = Query(None, description="Process pending draws for a specific category only.")):
    updated_draws_count = 0
    try:
        # Fetch all categories if no specific one is given, or just the one specified
        categories_to_check: List[LotteryCategory] = []
        if category_id:
            cat = get_category_db_by_id(category_id)
            if cat:
                categories_to_check.append(cat)
            else:
                raise HTTPException(status_code=404, detail=f"Category {category_id} not found.")
        else:
            categories_to_check = get_category_db_by_id(None) # Assuming this means get_all_categories
            # Correction: get_category_db_by_id(None) doesn't make sense.
            # Need to import and use get_all_categories from lottery_categories.db
            from lottery_categories.db import get_all_categories as get_all_lc_categories
            categories_to_check = get_all_lc_categories(active_only=True)


        now = datetime.utcnow()
        for category in categories_to_check:
            # Check for the next 'pending_open' draw for this category
            pending_draw = draws_db.get_next_pending_draw(category.id)
            if pending_draw and pending_draw.scheduled_open_time <= now:
                # If it's time to open this draw
                update_payload = DrawUpdate(status="open", actual_open_time=now)
                success = draws_db.update_draw(pending_draw.id, update_payload)
                if success:
                    updated_draws_count += 1
                    print(f"Draw {pending_draw.id} for category {category.name} opened.")
                    # Potentially create the *next* pending draw for this category
                    # This is where the scheduling loop would continue
                    # next_draw_create_payload = DrawCreate.from_category(category, start_time=pending_draw.scheduled_close_time)
                    # next_draw_id = draws_db.create_draw(next_draw_create_payload)
                    # if next_draw_id:
                    #    print(f"Created next pending draw {next_draw_id} for category {category.name}")
                    # else:
                    #    print(f"Failed to create next pending draw for category {category.name}")

        return {"message": f"Processed pending draws. {updated_draws_count} draw(s) opened."}

    except PyMongoError as e:
        print(f"PyMongoError in /process_pending_draws: {e}")
        raise HTTPException(status_code=500, detail="Database error while processing pending draws.")
    except Exception as e:
        print(f"Unexpected error in /process_pending_draws: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get('/category/{category_id}/current_open', response_model=List[Draw], summary="Get current open draws for a category")
def get_current_open_draws_for_category_endpoint(category_id: str):
    """
    Gets all currently open draws for a specific category.
    An "open" draw is one whose status is 'open', scheduled_open_time has passed,
    and scheduled_close_time has not yet passed.
    It's possible for multiple draws of the same category to be 'open' if their schedules overlap,
    though typically there would be one.
    """
    try:
        category = get_category_db_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Lottery category {category_id} not found.")

        open_draws = draws_db.get_open_draws_for_category(category_id)
        # If no open draws, and we want to auto-create one, this is where it would go.
        # For now, it just returns what's open. The ticket purchase logic will handle creation if needed.
        return open_draws
    except PyMongoError as e:
        print(f"PyMongoError in /category/{category_id}/current_open: {e}")
        raise HTTPException(status_code=500, detail="Database error fetching open draws.")
    except Exception as e:
        print(f"Unexpected error in /category/{category_id}/current_open: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error: {str(e)}")


@router.post('/close/{draw_id}', response_model=Draw, summary="Close an open draw and select a winner")
def close_draw_endpoint(draw_id: str):
    try:
        draw = draws_db.get_draw_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail=f"Draw with id {draw_id} not found.")

        now = datetime.utcnow()
        if draw.status == "completed" or draw.status == "closed": # Already processed
             return draw # Or raise error if trying to re-close
        if draw.status != "open" and draw.scheduled_close_time > now : # Not yet open or past close time
            raise HTTPException(status_code=400, detail=f"Draw {draw_id} is not yet ready to be closed or is not in 'open' state. Status: {draw.status}, Scheduled Close: {draw.scheduled_close_time}")

        # Fetch participants from the tickets collection for this draw_id
        ticket_collection = get_ticket_db_collection()
        # Ensure draw.id is string, which it should be from Pydantic model
        participants = list(ticket_collection.distinct("wallet_address", {"draw_id": draw.id}))

        update_payload: DrawUpdate
        if not participants:
            # No participants, so no winner, regardless of game type
            update_payload = DrawUpdate(
                status='completed',
                winners_by_tier=[], # Empty list for winners
                participants=[],
                actual_close_time=now
            )
        else:
            # Participants exist, proceed based on game type
            category = get_category_db_by_id(draw.category_id)
            if not category:
                raise HTTPException(status_code=500, detail=f"Category {draw.category_id} for draw {draw.id} not found during closing.")

            ledger_hash = get_latest_ledger_hash_sync() # Used for both raffle and as seed for PickN

            if category.game_type == "raffle":
                winner_idx = calculate_winner_index(ledger_hash, len(participants))
                # In a raffle, participants are wallet addresses. We need to find which ticket won.
                # This is a simplification: a raffle usually picks one ticket ID, not one participant.
                # For now, let's assume the participant IS the winner.
                # A true raffle winner would require fetching all ticket IDs for the draw and picking one.
                # Let's find one ticket_id for this winner for consistency with PrizeTierWinner model.
                winning_participant_wallet = participants[winner_idx]

                # Find a ticket associated with this winning participant for this draw
                # This is not ideal for true raffle, but fits current structure.
                winning_ticket_doc = ticket_collection.find_one(
                    {"draw_id": draw.id, "wallet_address": winning_participant_wallet},
                    {"_id": 1} # Get only the ticket ID
                )
                winning_ticket_id = str(winning_ticket_doc["_id"]) if winning_ticket_doc else "unknown_ticket"


                update_payload = DrawUpdate(
                    status='completed',
                    ledger_hash=ledger_hash,
                    winners_by_tier=[{ # PrizeTierWinner structure
                        "prize_tier_name": "Raffle Winner",
                        "wallet_address": winning_participant_wallet,
                        "ticket_id": winning_ticket_id
                    }],
                    participants=participants,
                    actual_close_time=now
                )
            elif category.game_type == "pick_n_digits":
                # 1. Generate winning numbers (RNG function to be created in next step)
                # Placeholder for now:
                # winning_numbers = rng_utils.generate_winning_picks(ledger_hash, category.game_config)
                # For testing, let's assume a fixed winning number generation if rng_utils is not ready
                # This MUST be replaced by the actual RNG call.

                # --- TEMPORARY Winning Number Generation ---
                temp_num_picks = category.game_config.get("num_picks", 3)
                winning_numbers_list = [int(d) for d in ledger_hash[:temp_num_picks] if d.isdigit()]
                while len(winning_numbers_list) < temp_num_picks: # Ensure enough digits
                    winning_numbers_list.append(0) # Pad with 0 if hash is too short
                winning_numbers_list = winning_numbers_list[:temp_num_picks]
                # --- END TEMPORARY ---

                current_winning_selection = {"picks": winning_numbers_list} # Example structure

                # 2. Find winning tickets (jackpot only for now)
                found_winners_for_tier: List[dict] = [] # Using dict to build PrizeTierWinner

                # Fetch all tickets for this draw that have selection_data
                draw_tickets = ticket_collection.find({"draw_id": draw.id, "selection_data": {"$exists": True}})

                for ticket_doc in draw_tickets:
                    ticket_selection = ticket_doc.get("selection_data", {}).get("picks")
                    if ticket_selection and list(ticket_selection) == winning_numbers_list: # Direct match for jackpot
                        found_winners_for_tier.append({
                            "prize_tier_name": f"Jackpot - Match {temp_num_picks}",
                            "wallet_address": ticket_doc["wallet_address"],
                            "ticket_id": str(ticket_doc["_id"])
                        })

                update_payload = DrawUpdate(
                    status='completed',
                    ledger_hash=ledger_hash, # Still useful as the seed
                    winning_selection=current_winning_selection,
                    winners_by_tier=found_winners_for_tier,
                    participants=participants, # All who bought tickets, not just winners
                    actual_close_time=now
                )
            else:
                raise HTTPException(status_code=500, detail=f"Unsupported game_type '{category.game_type}' for closing draw.")

        success = draws_db.update_draw(draw.id, update_payload)
        if not success:
            # Check if already updated by a concurrent request
            current_state = draws_db.get_draw_by_id(draw.id)
            if current_state and current_state.status == "completed":
                return current_state
            raise HTTPException(status_code=500, detail="Failed to update draw status to completed.")

        closed_draw = draws_db.get_draw_by_id(draw.id)
        if not closed_draw: # Should not happen
            raise HTTPException(status_code=500, detail="Failed to retrieve draw after closing.")

        # After closing, try to create the next draw for this category if rule applies
        category = get_category_db_by_id(closed_draw.category_id)
        if category and category.is_active and category.draw_interval_type != "manual":
            # Schedule next draw starting after the current one closes
            # Use scheduled_close_time of the just-closed draw as a basis for the next open time
            # to maintain cadence. If actual_close_time is much later, this could cause drift.
            # For more robust scheduling, a dedicated scheduler would track expected vs actual.
            next_start_time = closed_draw.scheduled_close_time
            try:
                next_draw_create_payload = DrawCreate.from_category(category, start_time=next_start_time)
                next_draw_id = draws_db.create_draw(next_draw_create_payload)
                if next_draw_id:
                    print(f"Successfully created next pending draw {next_draw_id} for category {category.name} after closing {draw_id}.")
                else:
                    print(f"Failed to create next pending draw for category {category.name} after closing {draw_id}.")
            except ValueError as ve: # from_category might raise this for bad interval type
                print(f"Error creating next draw for category {category.name}: {ve}")
            except Exception as e_next_draw: # Catch any other error during next draw creation
                print(f"Unexpected error creating next draw for category {category.name}: {e_next_draw}")

        return closed_draw

    except XRPLClientException as e:
        raise HTTPException(status_code=502, detail=f"Error communicating with XRPL: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error during draw closing: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get('/history', response_model=List[Draw], summary="Get history of draws, optionally filtered by category")
def draw_history_endpoint(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    limit: int = Query(20, gt=0, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    try:
        history = draws_db.get_draw_history(category_id=category_id, limit=limit, offset=offset)
        return history
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error fetching draw history: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error: {str(e)}")

@router.get('/{draw_id}', response_model=Draw, summary="Get a specific draw by its ID")
def get_draw_endpoint(draw_id: str):
    try:
        draw = draws_db.get_draw_by_id(draw_id)
        if draw is None:
            raise HTTPException(status_code=404, detail="Draw not found.")
        return draw
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error fetching draw: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error: {str(e)}")

# New endpoint to manually create a draw (e.g. for manual categories or specific scheduling)
@router.post("/", response_model=Draw, status_code=201, summary="Manually create a new draw")
def create_new_draw_endpoint(draw_in: DrawCreate):
    """
    Manually creates a new draw. Requires category_id, scheduled_open_time, and scheduled_close_time.
    Status defaults to 'pending_open'.
    """
    try:
        # Validate category_id exists
        category = get_category_db_by_id(draw_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail=f"Lottery category {draw_in.category_id} not found.")

        # Basic validation for times
        if draw_in.scheduled_open_time >= draw_in.scheduled_close_time:
            raise HTTPException(status_code=400, detail="Scheduled open time must be before scheduled close time.")

        draw_id = draws_db.create_draw(draw_in)
        if not draw_id:
            raise HTTPException(status_code=500, detail="Failed to create draw in database.")

        created_draw = draws_db.get_draw_by_id(draw_id)
        if not created_draw:
            raise HTTPException(status_code=500, detail="Failed to retrieve created draw.")
        return created_draw
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error creating draw: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error: {str(e)}")
