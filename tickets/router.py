from fastapi import APIRouter, HTTPException, Depends
from .models import TicketPurchaseRequest, TicketPurchaseResponse, TicketEntry, TicketCreate
from . import db as tickets_db
from draws import db as draws_db # Import draw DB functions
from draws.models import DrawCreate as DrawCreateSchema # To create a new draw if needed
from datetime import datetime
from typing import List
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/buy", response_model=TicketPurchaseResponse)
def buy_tickets(req: TicketPurchaseRequest):
    if req.num_tickets < 1:
        raise HTTPException(status_code=400, detail="Must buy at least one ticket.")

    current_draw_id: str
    try:
        # Get the current open draw
        open_draw = draws_db.get_open_draw()
        if not open_draw:
            # If no draw is open, create a new one
            new_draw_data = DrawCreateSchema() # Use the schema for creation
            created_draw_id = draws_db.create_draw(new_draw_data)
            if not created_draw_id:
                raise HTTPException(status_code=500, detail="Failed to create a new draw for ticket purchase.")
            current_draw_id = created_draw_id
            # Optionally, we might want to add the buyer as the first participant if draws_db.create_draw doesn't handle it
            # For now, participants are added when tickets are linked or draw is closed.
        else:
            if open_draw.id is None: # Should not happen if data is consistent
                 raise HTTPException(status_code=500, detail="Open draw found but has no ID.")
            current_draw_id = open_draw.id
    except PyMongoError as e:
        print(f"PyMongoError when fetching/creating draw for ticket purchase: {e}")
        raise HTTPException(status_code=500, detail="Database error while preparing for ticket purchase.")
    except Exception as e:
        print(f"Unexpected error when fetching/creating draw for ticket purchase: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while preparing for ticket purchase.")


    purchased_ticket_ids = []
    for _ in range(req.num_tickets):
        ticket_to_create = TicketCreate(
            wallet_address=req.wallet_address,
            draw_id=current_draw_id, # Using placeholder for now
            timestamp=datetime.utcnow()
        )
        try:
            ticket_id = tickets_db.create_ticket(ticket_to_create)
            if ticket_id:
                purchased_ticket_ids.append(ticket_id)
            else:
                # This indicates a problem with ticket creation in the DB layer
                raise HTTPException(status_code=500, detail="Failed to save ticket to database.")
        except PyMongoError as e:
            # Log the error e
            print(f"PyMongoError during ticket purchase: {e}")
            raise HTTPException(status_code=500, detail="An error occurred with the database while purchasing tickets.")
        except Exception as e:
            # Log the error e
            print(f"Unexpected error during ticket purchase: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while purchasing tickets.")


    if not purchased_ticket_ids or len(purchased_ticket_ids) != req.num_tickets:
        # This case might occur if some tickets failed to save but no exception was raised from db layer,
        # or if num_tickets was valid but loop didn't run as expected.
        raise HTTPException(status_code=500, detail="Could not purchase all requested tickets.")

    return TicketPurchaseResponse(
        success=True,
        message=f"{len(purchased_ticket_ids)} tickets purchased successfully.",
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
