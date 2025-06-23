from pydantic import BaseModel
from typing import List

class TicketPurchaseRequest(BaseModel):
    wallet_address: str
    num_tickets: int

class TicketPurchaseResponse(BaseModel):
    success: bool
    message: str
    tickets: List[int] = []

class TicketEntry(BaseModel):
    ticket_id: int
    wallet_address: str
    draw_id: int
    timestamp: str
