from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.errors import PyMongoError
from bson import ObjectId

from database import get_db
from .models import TicketCreate, TicketEntry # Assuming TicketEntry can represent a ticket from DB

def get_tickets_collection() -> Collection:
    """Returns the 'tickets' collection from MongoDB."""
    db = get_db()
    return db.tickets

def create_ticket(ticket_data: TicketCreate) -> str | None:
    """
    Creates a new ticket in the database.
    Args:
        ticket_data: TicketCreate model instance.
    Returns:
        The ID of the newly created ticket as a string, or None if creation failed.
    """
    try:
        collection = get_tickets_collection()
        # Pydantic model_dump is used for Pydantic V2
        # For V1, it's .dict()
        result: InsertOneResult = collection.insert_one(ticket_data.model_dump())
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Error creating ticket in MongoDB: {e}")
        return None

def get_tickets_by_wallet(wallet_address: str) -> list[TicketEntry]:
    """
    Retrieves all tickets for a given wallet address.
    Args:
        wallet_address: The wallet address to search for.
    Returns:
        A list of TicketEntry objects.
    """
    tickets = []
    try:
        collection = get_tickets_collection()
        db_tickets = collection.find({"wallet_address": wallet_address})
        for t_data in db_tickets:
            t_data['_id'] = str(t_data['_id']) # Convert ObjectId to str for the model
            # Ensure draw_id is also string if it's an ObjectId from DB
            if isinstance(t_data.get('draw_id'), ObjectId):
                t_data['draw_id'] = str(t_data['draw_id'])
            tickets.append(TicketEntry(**t_data))
        return tickets
    except PyMongoError as e:
        print(f"Error retrieving tickets by wallet from MongoDB: {e}")
        return [] # Return empty list on error

def get_ticket_by_id(ticket_id: str) -> TicketEntry | None:
    """
    Retrieves a single ticket by its ID.
    Args:
        ticket_id: The ID of the ticket (as a string).
    Returns:
        A TicketEntry object if found, otherwise None.
    """
    try:
        collection = get_tickets_collection()
        if not ObjectId.is_valid(ticket_id):
            return None # Invalid ObjectId format
        db_ticket = collection.find_one({"_id": ObjectId(ticket_id)})
        if db_ticket:
            db_ticket['_id'] = str(db_ticket['_id'])
            if isinstance(db_ticket.get('draw_id'), ObjectId):
                db_ticket['draw_id'] = str(db_ticket['draw_id'])
            return TicketEntry(**db_ticket)
        return None
    except PyMongoError as e:
        print(f"Error retrieving ticket by ID from MongoDB: {e}")
        return None
    except Exception as e: # Catch potential ObjectId conversion errors too
        print(f"Error converting ticket ID or processing ticket data: {e}")
        return None

# The global ticket_db list and get_next_ticket_id are no longer needed.
# ticket_db: List[TicketEntry] = []
# ticket_counter = 1

# def get_next_ticket_id():
#     global ticket_counter
#     ticket_id = ticket_counter
#     ticket_counter += 1
#     return ticket_id
