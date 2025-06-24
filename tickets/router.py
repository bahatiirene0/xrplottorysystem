from fastapi import APIRouter, HTTPException, Depends
from .models import TicketPurchaseRequest, TicketPurchaseResponse, TicketEntry, TicketCreate
from . import db as tickets_db
from draws import db as draws_db
from draws.models import DrawCreate as DrawCreateSchema, DrawUpdate as DrawUpdateSchema, Draw as DrawSchema
from lottery_categories.db import get_category_by_id as get_category_db_by_id
from datetime import datetime
from typing import List
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/buy", response_model=TicketPurchaseResponse) # Route could be /buy or /categories/{category_id}/buy
def buy_tickets(req: TicketPurchaseRequest):
    if req.num_tickets < 1:
        raise HTTPException(status_code=400, detail="Must buy at least one ticket.")

    active_draw_id: str
    try:
        # 1. Validate Category
        category = get_category_db_by_id(req.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Lottery category {req.category_id} not found.")
        if not category.is_active:
            raise HTTPException(status_code=400, detail=f"Lottery category {req.category_id} is not active.")

        # 2. Find an open draw for this category
        open_draws = draws_db.get_open_draws_for_category(req.category_id)

        target_draw: Optional[DrawSchema] = None
        if open_draws:
            target_draw = open_draws[0] # Pick the one closing soonest (it's sorted)

        if not target_draw:
            # If no open draw, try to create one based on category schedule
            # This implies the draw should start now or very soon.
            # We might need to check if a "pending_open" draw exists that should be opened first.
            # This logic can get complex if a scheduler isn't running to manage draw state.

            # Let's first check if there's a pending draw that should be opened now
            now = datetime.utcnow()
            next_pending = draws_db.get_next_pending_draw(req.category_id)
            if next_pending and next_pending.scheduled_open_time <= now:
                # Open this pending draw
                update_res = draws_db.update_draw(next_pending.id, DrawUpdateSchema(status="open", actual_open_time=now))
                if update_res:
                    target_draw = draws_db.get_draw_by_id(next_pending.id)
                else:
                    raise HTTPException(status_code=500, detail="Failed to open a pending draw for ticket purchase.")

            if not target_draw: # Still no target_draw, so create a new one
                if category.draw_interval_type == "manual":
                     raise HTTPException(status_code=400, detail=f"Category {category.name} is manual. No open draw available and new draws must be created manually.")

                try:
                    # Create a new draw that starts now.
                    new_draw_payload = DrawCreateSchema.from_category(category, start_time=now)
                    # Override status to "open" as it's being created for immediate ticket sales
                    new_draw_payload.status = "open"

                    created_draw_id = draws_db.create_draw(new_draw_payload)
                    if not created_draw_id:
                        raise HTTPException(status_code=500, detail="Failed to create a new draw for ticket purchase.")

                    # Set actual_open_time for the newly created and opened draw
                    draws_db.update_draw(created_draw_id, DrawUpdateSchema(actual_open_time=now))
                    target_draw = draws_db.get_draw_by_id(created_draw_id)

                except ValueError as ve: # from_category might raise this
                    raise HTTPException(status_code=400, detail=f"Cannot create draw: {str(ve)}")


        if not target_draw or target_draw.id is None:
            # This should ideally be caught by earlier logic
            raise HTTPException(status_code=500, detail="Could not find or create an active draw for the category.")

        if target_draw.status != "open":
             raise HTTPException(status_code=400, detail=f"The current draw {target_draw.id} for category {category.name} is not open for ticket sales. Status: {target_draw.status}")

        active_draw_id = target_draw.id

    except PyMongoError as e:
        print(f"PyMongoError when fetching/creating draw for ticket purchase: {e}")
        raise HTTPException(status_code=500, detail="Database error while preparing for ticket purchase.")
    except HTTPException:
        raise # Re-raise HTTPExceptions directly
    except Exception as e:
        print(f"Unexpected error when fetching/creating draw for ticket purchase: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    purchased_ticket_ids = []
    for _ in range(req.num_tickets):
        ticket_to_create = TicketCreate(
            wallet_address=req.wallet_address,
            draw_id=active_draw_id,
            timestamp=datetime.utcnow() # This timestamp is for the ticket itself
        )
        try:
            # Optional: Check if ticket price from category matches something if it were in request
            # For now, ticket price is on category, not per ticket request.

            ticket_id = tickets_db.create_ticket(ticket_to_create)
            if ticket_id:
                purchased_ticket_ids.append(ticket_id)
                # Optionally, add participant to draw document in real-time (can be slow for many tickets)
                # draws_db.add_participant_to_draw(active_draw_id, req.wallet_address)
            else:
                raise HTTPException(status_code=500, detail="Failed to save one or more tickets to database.")
        except PyMongoError as e:
            print(f"PyMongoError during ticket purchase (saving ticket): {e}")
            # Decide on rollback strategy or partial success if some tickets are saved.
            # For now, fail the whole batch if one ticket fails.
            raise HTTPException(status_code=500, detail="Database error while saving a ticket.")
        except Exception as e:
            print(f"Unexpected error during ticket purchase (saving ticket): {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while saving a ticket.")

    if not purchased_ticket_ids or len(purchased_ticket_ids) != req.num_tickets:
        # This implies some failure that didn't raise an exception or partial processing.
        # Should be rare if exceptions are raised correctly above.
        raise HTTPException(status_code=500, detail="Could not purchase all requested tickets. Partial transaction may have occurred.")

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
