from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import Draw, DrawCreate, DrawUpdate
from tickets.db import get_tickets_collection as get_ticket_db_collection
from rng.utils import calculate_winner_index
from datetime import datetime
from xrpl.clients import JsonRpcClient
# TODO: Find correct import for XRPLClientException for xrpl-py==2.4.0 and reinstate
# from xrpl.clients import XRPLClientException # This was one attempt
# from xrpl.exceptions import XRPLClientException # This was another
# from xrpl import XRPLClientException # And another
from xrpl.models.requests.ledger import Ledger
import os
import logging # Added logging

from . import db as draws_db
from lottery_categories.db import get_category_by_id as get_category_db_by_id, update_category_rollover # Import added
from lottery_categories.models import LotteryCategory, PrizeTierConfig # Added PrizeTierConfig
from .models import PrizeTierWinner # Added PrizeTierWinner for type hinting
from pymongo.errors import PyMongoError

router = APIRouter()
logger = logging.getLogger(__name__) # Added logger

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
            # TODO: Replace Exception with specific XRPLClientException once import is resolved
            raise Exception(f"Failed to get ledger_hash: {error_message}")
        return result.get('ledger_hash')
    # TODO: Reinstate specific XRPLClientException catch once import is resolved
    # except XRPLClientException as e:
    #     print(f"XRPLClientException in get_latest_ledger_hash_sync: {e}")
    #     raise
    except Exception as e: # Catching generic Exception for now
        print(f"Exception in get_latest_ledger_hash_sync: {e}")
        # TODO: Replace Exception with specific XRPLClientException once import is resolved
        raise Exception(f"An unexpected error occurred while fetching ledger hash: {e}")


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
                # --- Updated Raffle Logic for Tiers ---
                winners_for_final_payload: List[Dict[str, Any]] = []

                # Fetch all tickets for the draw, not just distinct participants, as tickets are unique entries.
                all_raffle_ticket_docs = list(ticket_collection.find(
                    {"draw_id": draw.id},
                    {"_id": 1, "wallet_address": 1} # Get ID and wallet address
                ))

                if not all_raffle_ticket_docs:
                    # No tickets sold for the raffle, complete draw with no winners
                    # participants list would be empty, so this is covered by the initial check.
                    # However, if participants list is NOT empty but all_raffle_ticket_docs IS empty (data inconsistency),
                    # this logic is a safeguard for winner selection.
                    # The initial `if not participants:` check should handle this.
                    # For safety, we can ensure winners_by_tier is empty.
                    logger.info(f"No tickets found for raffle draw {draw.id}, though participants list was not empty. Setting no winners.")
                    update_payload = DrawUpdate(status='completed', winners_by_tier=[], participants=participants, actual_close_time=now, ledger_hash=ledger_hash)

                else:
                    # Use a copy of tickets to draw from, to ensure unique winners per tier
                    drawable_tickets = [
                        {"ticket_id": str(t["_id"]), "wallet_address": t["wallet_address"]}
                        for t in all_raffle_ticket_docs
                    ]

                    picked_ticket_ids_for_draw = set()

                    # Assuming category.prize_tiers is already sorted in the desired order of awarding (e.g., highest prize first)
                    for tier_config in category.prize_tiers:
                        if not drawable_tickets:
                            logger.info(f"No more drawable tickets for tier {tier_config.tier_name} in draw {draw.id}")
                            break

                        # Determine number of winners for THIS tier.
                        # For typical raffles, this is 1 winner per tier_config entry.
                        # If a tier_config could specify multiple winners for that single tier (e.g. 5 winners for "Tier 3"),
                        # this loop would need to run multiple times for this tier_config.
                        # For now, assume 1 winner per tier_config object.

                        # Vary seed per tier/pick to ensure different outcomes if multiple winners are picked from the same list
                        # Using tier_name and number of already picked winners to ensure unique seed component.
                        current_pick_seed_modifier = f"{tier_config.tier_name}_{len(picked_ticket_ids_for_draw)}"
                        winner_idx = calculate_winner_index(f"{ledger_hash}_{current_pick_seed_modifier}", len(drawable_tickets))

                        selected_winner_ticket_info = drawable_tickets.pop(winner_idx)

                        # The pop ensures this ticket won't be drawn again for subsequent tiers.
                        # picked_ticket_ids_for_draw ensures a ticket doesn't win twice if somehow drawable_tickets wasn't managed perfectly (defensive).
                        if selected_winner_ticket_info["ticket_id"] in picked_ticket_ids_for_draw:
                             logger.warning(f"Ticket {selected_winner_ticket_info['ticket_id']} was already picked. This indicates an issue. Skipping for tier {tier_config.tier_name}.")
                             continue

                        picked_ticket_ids_for_draw.add(selected_winner_ticket_info["ticket_id"])

                        prize_amount_for_tier_winner: float
                        is_fixed = False
                        if tier_config.fixed_prize_amount is not None:
                            prize_amount_for_tier_winner = tier_config.fixed_prize_amount
                            is_fixed = True
                        elif tier_config.percentage_of_prize_pool is not None:
                            total_pool_for_this_tier = (tier_config.percentage_of_prize_pool / 100.0) * draw.base_prize_pool
                            # For raffles, typically 1 winner per tier config, so no division unless tier_config allows multiple winners for this specific tier.
                            prize_amount_for_tier_winner = total_pool_for_this_tier
                            is_fixed = False
                        else:
                            # This should be caught by LotteryCategory model validation
                            logger.error(f"Raffle Tier {tier_config.tier_name} in category {category.id} has neither fixed nor percentage prize. Skipping.")
                            continue

                        winners_for_final_payload.append({
                            "tier_name": tier_config.tier_name,
                            "wallet_address": selected_winner_ticket_info["wallet_address"],
                            "ticket_id": selected_winner_ticket_info["ticket_id"],
                            "prize_amount_calculated": round(prize_amount_for_tier_winner, 2),
                            "is_fixed_prize": is_fixed,
                            "fee_amount_charged": round((prize_amount_for_tier_winner * category.winner_fee_percentage / 100.0), 2),
                            "net_prize_payable": round(prize_amount_for_tier_winner * (1 - category.winner_fee_percentage / 100.0), 2)
                        })

                    update_payload = DrawUpdate(
                        status='completed',
                        ledger_hash=ledger_hash,
                        winners_by_tier=winners_for_final_payload,
                        participants=participants,
                        actual_close_time=now
                    )
            elif category.game_type == "pick_n_digits":
                # 1. Generate winning numbers using the proper RNG utility
                if not category.game_config: # Should be validated at category creation
                    raise HTTPException(status_code=500, detail=f"Category {category.id} is missing game_config for Pick N game.")

                # Ensure rng.utils is imported
                from rng.utils import generate_winning_picks # Moved import here for clarity

                try:
                    winning_numbers_list = generate_winning_picks(seed=ledger_hash, game_config=category.game_config)
                except ValueError as e:
                    raise HTTPException(status_code=500, detail=f"Error generating winning numbers: {str(e)}")

                current_winning_selection = {"picks": winning_numbers_list}
                processed_winners_by_tier: List[PrizeTierWinner] = []

                # Fetch all tickets for this draw that have selection_data
                # And group them by number of matches for efficiency if possible, or iterate
                # For now, iterate and check each tier.

                all_draw_tickets_cursor = ticket_collection.find({"draw_id": draw.id, "selection_data": {"$exists": True}})

                # Collect all tickets to allow multiple checks if a ticket wins in multiple (lower) tiers (if rules allow)
                # Or, more commonly, a ticket wins in the highest possible tier it qualifies for.
                # Let's assume a ticket wins in the BEST tier it qualifies for.

                # Pre-calculate matches for each ticket
                ticket_matches_info = []
                for ticket_doc in all_draw_tickets_cursor:
                    user_picks = ticket_doc.get("selection_data", {}).get("picks")
                    if user_picks:
                        # Count matches (order might matter or not based on game_config)
                        # Assuming order doesn't matter and picks are unique in winning_numbers_list for simplicity here.
                        # A more robust match count would depend on game_config (e.g., allow_duplicates in user_picks vs winning_numbers)
                        matches = len(set(user_picks) & set(winning_numbers_list))
                        ticket_matches_info.append({
                            "ticket_id": str(ticket_doc["_id"]),
                            "wallet_address": ticket_doc["wallet_address"],
                            "matches": matches
                        })

                # Sort tiers by matches_required descending (or by prize amount) to award best tier first
                sorted_tiers = sorted(
                    [tier for tier in category.prize_tiers if tier.matches_required is not None],
                    key=lambda t: t.matches_required,
                    reverse=True
                )

                winners_for_final_payload: List[Dict[str, Any]] = [] # To build PrizeTierWinner later

                # This list will store tuples of (tier_name, wallet_address, ticket_id, prize_amount, is_fixed)
                # This is a temporary list to hold potential winners before splitting prize pool for percentage tiers
                tier_winners_intermediate: Dict[str, List[Dict]] = {tier.tier_name: [] for tier in sorted_tiers}


                for ticket_info in ticket_matches_info:
                    for tier_config in sorted_tiers:
                        if ticket_info["matches"] >= tier_config.matches_required:
                            # This ticket qualifies for this tier. Add to intermediate list for this tier.
                            tier_winners_intermediate[tier_config.tier_name].append({
                                "wallet_address": ticket_info["wallet_address"],
                                "ticket_id": ticket_info["ticket_id"],
                                # prize_amount and is_fixed_prize to be determined next
                            })
                            break # Award only the best tier qualified for


                # Calculate prize amounts and populate processed_winners_by_tier
                for tier_config in category.prize_tiers: # Iterate in original order or sorted by value
                    winners_in_this_tier = tier_winners_intermediate.get(tier_config.tier_name, [])
                    if not winners_in_this_tier:
                        continue

                    prize_amount_for_tier_winner: float
                    is_fixed = False
                    if tier_config.fixed_prize_amount is not None:
                        prize_amount_for_tier_winner = tier_config.fixed_prize_amount
                        is_fixed = True
                    elif tier_config.percentage_of_prize_pool is not None:
                        # draw.base_prize_pool should be available here
                        total_pool_for_this_tier = (tier_config.percentage_of_prize_pool / 100.0) * draw.base_prize_pool
                        if winners_in_this_tier: # Avoid division by zero, though check already there
                            prize_amount_for_tier_winner = total_pool_for_this_tier / len(winners_in_this_tier)
                        else:
                            prize_amount_for_tier_winner = 0 # Should not happen if winners_in_this_tier is populated
                        is_fixed = False
                    else:
                        # This case should be prevented by model validation
                        logger.error(f"Tier {tier_config.tier_name} has neither fixed nor percentage prize. Skipping.")
                        continue

                    for winner_data in winners_in_this_tier:
                        winners_for_final_payload.append({
                            "tier_name": tier_config.tier_name,
                            "wallet_address": winner_data["wallet_address"],
                            "ticket_id": winner_data["ticket_id"],
                            "prize_amount_calculated": round(prize_amount_for_tier_winner, 2),
                            "is_fixed_prize": is_fixed,
                            "fee_amount_charged": round((prize_amount_for_tier_winner * category.winner_fee_percentage / 100.0), 2),
                            "net_prize_payable": round(prize_amount_for_tier_winner * (1 - category.winner_fee_percentage / 100.0), 2)
                        })

                update_payload = DrawUpdate(
                    status='completed',
                    ledger_hash=ledger_hash,
                    winning_selection=current_winning_selection,
                    winners_by_tier=winners_for_final_payload, # This will be list of dicts, Pydantic handles conversion
                    participants=participants,
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

        # --- Progressive Jackpot Logic ---
        # This happens after the draw is successfully closed and winners (if any) are determined.
        # We need the 'category' object again, and the 'winners_for_final_payload' (or equivalent from 'closed_draw').
        if category: # Ensure category was fetched successfully earlier
            category_updated_for_rollover = False
            new_rollover_amount = category.current_rollover_amount # Start with current category rollover

            # Check if a jackpot tier that *would have received* rollover was won.
            # If so, the category's rollover should be reset.
            jackpot_tier_won = False
            if closed_draw and closed_draw.winners_by_tier:
                for winner_entry in closed_draw.winners_by_tier:
                    # Find corresponding tier_config for this winner_entry.tier_name
                    tier_cfg_for_winner = next((tc for tc in category.prize_tiers if tc.tier_name == winner_entry.tier_name), None)
                    if tier_cfg_for_winner and tier_cfg_for_winner.is_jackpot_tier: # Assuming is_jackpot_tier implies it received rollover
                        jackpot_tier_won = True
                        break

            if jackpot_tier_won:
                if new_rollover_amount > 0 : # Only reset if there was something to win from rollover
                    logger.info(f"Jackpot tier won for category {category.id}. Resetting rollover amount from {new_rollover_amount} to 0.")
                    new_rollover_amount = 0.0 # Reset rollover
                    category_updated_for_rollover = True

            # If jackpot was NOT won (or no jackpot tier defined as such), then check for contributions to rollover.
            if not jackpot_tier_won:
                for tier_config in category.prize_tiers:
                    if tier_config.contributes_to_rollover_if_unwon:
                        # Check if this tier had any winners in the current draw
                        tier_had_winners = False
                        if closed_draw and closed_draw.winners_by_tier:
                            for winner_entry in closed_draw.winners_by_tier:
                                if winner_entry.tier_name == tier_config.tier_name:
                                    tier_had_winners = True
                                    break

                        if not tier_had_winners:
                            # Tier was not won, calculate its contribution to rollover
                            # Contribution is based on the category's base prize pool, not the draw's (which included previous rollover)
                            contribution_to_rollover = 0.0
                            if tier_config.fixed_prize_amount is not None:
                                contribution_to_rollover = tier_config.fixed_prize_amount
                            elif tier_config.percentage_of_prize_pool is not None:
                                contribution_to_rollover = (tier_config.percentage_of_prize_pool / 100.0) * category.base_prize_pool

                            if contribution_to_rollover > 0:
                                new_rollover_amount += contribution_to_rollover
                                category_updated_for_rollover = True
                                logger.info(f"Tier '{tier_config.tier_name}' not won in draw {draw.id}. Adding {contribution_to_rollover} to rollover for category {category.id}. New total rollover: {new_rollover_amount}")

            if category_updated_for_rollover:
                update_success = update_category_rollover(category.id, new_rollover_amount) # Use directly imported function
                if not update_success:
                    logger.error(f"Failed to update rollover amount for category {category.id} to {new_rollover_amount}.")
                    # This is a non-critical error for the draw closing itself, but should be monitored.
        # --- End Progressive Jackpot Logic ---

        return closed_draw

    # TODO: Reinstate specific XRPLClientException catch once import is resolved
    # except XRPLClientException as e:
    #     raise HTTPException(status_code=502, detail=f"Error communicating with XRPL: {str(e)}")
    except PyMongoError as e: # PyMongoError should be caught before generic Exception
        raise HTTPException(status_code=500, detail=f"Database error during draw closing: {str(e)}")
    except HTTPException: # Re-raise other HTTPExceptions
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
