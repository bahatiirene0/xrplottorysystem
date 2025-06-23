from fastapi import APIRouter, HTTPException
from .models import TicketPurchaseRequest, TicketPurchaseResponse, TicketEntry
from .db import ticket_db, get_next_ticket_id
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/buy", response_model=TicketPurchaseResponse)
def buy_tickets(req: TicketPurchaseRequest):
    if req.num_tickets < 1:
        raise HTTPException(status_code=400, detail="Must buy at least one ticket.")
    tickets = []
    for _ in range(req.num_tickets):
        ticket = TicketEntry(
            ticket_id=get_next_ticket_id(),
            wallet_address=req.wallet_address,
            draw_id=1,  # Placeholder, should be current draw
            timestamp=datetime.utcnow().isoformat()
        )
        ticket_db.append(ticket)
        tickets.append(ticket.ticket_id)
    return TicketPurchaseResponse(success=True, message="Tickets purchased.", tickets=tickets)

@router.get("/list/{wallet_address}", response_model=List[TicketEntry])
def list_tickets(wallet_address: str):
    return [t for t in ticket_db if t.wallet_address == wallet_address]
