from fastapi import APIRouter, HTTPException
from .models import Draw, DrawCreate, DrawUpdate
# We need to get participants from tickets associated with this draw, not all tickets.
# from tickets.db import get_tickets_for_draw # This function would need to be created
from tickets.db import get_tickets_collection as get_ticket_db_collection # to query tickets for a draw
from rng.utils import calculate_winner_index
from datetime import datetime
from xrpl.clients import JsonRpcClient
from xrpl.models.requests.ledger import Ledger
from xrpl.asyncio.clients import AsyncJsonRpcClient # For async client if we go async
from xrpl.clients.exceptions import XRPLClientException
import os

from . import db as draws_db # Import new DB functions
from pymongo.errors import PyMongoError

router = APIRouter()

XRPL_RPC_URL = os.environ.get('XRPL_RPC_URL', 'https://s.altnet.rippletest.net:51234/')

def get_latest_ledger_hash_sync(): # Renamed to avoid conflict if we add async later
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
    except Exception as e: # Catch other potential issues like network problems
        print(f"Generic Exception in get_latest_ledger_hash_sync: {e}")
        raise XRPLClientException(f"An unexpected error occurred while fetching ledger hash: {e}")


@router.get('/current', response_model=Draw)
def get_current_draw_endpoint():
    try:
        current_draw = draws_db.get_open_draw()
        if not current_draw:
            # Create a new draw if no open draw exists
            new_draw_data = DrawCreate()
            new_draw_id = draws_db.create_draw(new_draw_data)
            if not new_draw_id:
                raise HTTPException(status_code=500, detail="Failed to create a new draw.")
            current_draw = draws_db.get_draw_by_id(new_draw_id)
            if not current_draw: # Should not happen if create_draw was successful
                 raise HTTPException(status_code=500, detail="Failed to retrieve newly created draw.")
        return current_draw
    except PyMongoError as e:
        print(f"PyMongoError in /current draw endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching current draw.")
    except Exception as e:
        print(f"Unexpected error in /current draw endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.post('/close/{draw_id}', response_model=Draw) # Changed to take draw_id
def close_draw_endpoint(draw_id: str):
    try:
        draw = draws_db.get_draw_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail=f"Draw with id {draw_id} not found.")
        if draw.status != "open":
            raise HTTPException(status_code=400, detail=f"Draw {draw_id} is not open. Current status: {draw.status}")

        # Fetch participants for this specific draw_id from the tickets collection
        ticket_collection = get_ticket_db_collection()
        # Distinct query to get unique wallet_addresses for this draw_id
        # Ensure draw_id in tickets is stored as a string if draw.id is a string.
        participants = list(ticket_collection.distinct("wallet_address", {"draw_id": draw.id}))

        if not participants:
            update_data = DrawUpdate(status='completed', winner=None, participants=[])
            draws_db.update_draw(draw.id, update_data)
            updated_draw = draws_db.get_draw_by_id(draw.id)
            if not updated_draw:
                 raise HTTPException(status_code=500, detail="Failed to update draw after no participants.")
            return updated_draw # Or a specific message dict

        ledger_hash = get_latest_ledger_hash_sync()
        if not ledger_hash: # Should be caught by exception in function now
            raise HTTPException(status_code=500, detail='Could not fetch XRPL ledger hash')

        winner_idx = calculate_winner_index(ledger_hash, len(participants))
        winner_wallet = participants[winner_idx]

        update_data = DrawUpdate(
            status='completed',
            ledger_hash=ledger_hash,
            winner=winner_wallet,
            participants=participants # Save the actual participants at close time
        )
        success = draws_db.update_draw(draw.id, update_data)
        if not success:
            # This might happen if the draw was modified/deleted between fetch and update
            # or if update_draw has an issue not raising PyMongoError
            existing_draw_check = draws_db.get_draw_by_id(draw.id)
            if existing_draw_check and existing_draw_check.status == "completed":
                 # it might have been updated by a concurrent request
                 return existing_draw_check
            raise HTTPException(status_code=500, detail="Failed to update draw status to completed.")

        closed_draw = draws_db.get_draw_by_id(draw.id)
        if not closed_draw:
            raise HTTPException(status_code=500, detail="Failed to retrieve draw after closing.")
        return closed_draw

    except XRPLClientException as e:
        print(f"XRPLClientException in /close draw endpoint: {e}")
        raise HTTPException(status_code=502, detail=f"Error communicating with XRPL: {str(e)}")
    except PyMongoError as e:
        print(f"PyMongoError in /close draw endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error during draw closing.")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Unexpected error in /close draw endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get('/history', response_model=list[Draw])
def draw_history_endpoint():
    try:
        history = draws_db.get_draw_history()
        return history
    except PyMongoError as e:
        print(f"PyMongoError in /history endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching draw history.")
    except Exception as e:
        print(f"Unexpected error in /history endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get('/{draw_id}', response_model=Draw)
def get_draw_endpoint(draw_id: str):
    try:
        draw = draws_db.get_draw_by_id(draw_id)
        if draw is None:
            raise HTTPException(status_code=404, detail="Draw not found.")
        return draw
    except PyMongoError as e:
        print(f"PyMongoError in GET /{draw_id} endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching draw.")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Unexpected error in GET /{draw_id} endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
