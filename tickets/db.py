from typing import List
from tickets.models import TicketEntry

ticket_db: List[TicketEntry] = []
ticket_counter = 1

def get_next_ticket_id():
    global ticket_counter
    ticket_id = ticket_counter
    ticket_counter += 1
    return ticket_id
