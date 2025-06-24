from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import List, Dict, Any

from database import get_db
from .models import Draw, DrawCreate, DrawUpdate # Draw is used to represent a draw from DB

def get_draws_collection() -> Collection:
    """Returns the 'draws' collection from MongoDB."""
    db = get_db()
    return db.draws

def create_draw(draw_data: DrawCreate) -> str | None:
    """
    Creates a new draw in the database.
    Args:
        draw_data: DrawCreate model instance.
    Returns:
        The ID (str) of the newly created draw, or None if creation failed.
    """
    try:
        collection = get_draws_collection()
        result: InsertOneResult = collection.insert_one(draw_data.model_dump())
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Error creating draw in MongoDB: {e}")
        return None

def get_draw_by_id(draw_id: str) -> Draw | None:
    """
    Retrieves a single draw by its ID.
    Args:
        draw_id: The ID of the draw (string).
    Returns:
        A Draw object if found, otherwise None.
    """
    try:
        collection = get_draws_collection()
        if not ObjectId.is_valid(draw_id):
            return None # Invalid ObjectId format
        db_draw = collection.find_one({"_id": ObjectId(draw_id)})
        if db_draw:
            # Convert ObjectId to str for Pydantic model
            db_draw['_id'] = str(db_draw['_id'])
            return Draw(**db_draw)
        return None
    except PyMongoError as e:
        print(f"Error retrieving draw by ID from MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error converting draw ID or processing draw data: {e}")
        return None

def get_open_draw() -> Draw | None:
    """
    Retrieves the first draw with status 'open'.
    Returns:
        A Draw object if an open draw is found, otherwise None.
    """
    try:
        collection = get_draws_collection()
        db_draw = collection.find_one({"status": "open"})
        if db_draw:
            db_draw['_id'] = str(db_draw['_id'])
            return Draw(**db_draw)
        return None
    except PyMongoError as e:
        print(f"Error retrieving open draw from MongoDB: {e}")
        return None

def update_draw(draw_id: str, update_data: DrawUpdate) -> bool:
    """
    Updates a draw in the database.
    Args:
        draw_id: The ID of the draw to update.
        update_data: DrawUpdate model instance with fields to update.
    Returns:
        True if update was successful, False otherwise.
    """
    try:
        collection = get_draws_collection()
        if not ObjectId.is_valid(draw_id):
            return False

        # model_dump with exclude_unset=True ensures only provided fields are updated
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return True # Nothing to update

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(draw_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating draw in MongoDB: {e}")
        return False

def get_draw_history() -> list[Draw]:
    """
    Retrieves all draws, ordered by timestamp descending.
    Returns:
        A list of Draw objects.
    """
    draws = []
    try:
        collection = get_draws_collection()
        # Sort by timestamp descending to get latest draws first
        db_draws = collection.find().sort("timestamp", -1)
        for d_data in db_draws:
            d_data['_id'] = str(d_data['_id'])
            draws.append(Draw(**d_data))
        return draws
    except PyMongoError as e:
        print(f"Error retrieving draw history from MongoDB: {e}")
        return []

def get_participants_for_draw(draw_id: str) -> List[str] | None:
    """
    Retrieves the list of participant wallet addresses for a specific draw.
    Args:
        draw_id: The ID of the draw.
    Returns:
        A list of wallet addresses or None if draw not found or error.
    """
    try:
        draw = get_draw_by_id(draw_id)
        if draw:
            return draw.participants
        return None
    except PyMongoError as e:
        print(f"Error retrieving participants for draw {draw_id}: {e}")
        return None

def add_participant_to_draw(draw_id: str, wallet_address: str) -> bool:
    """
    Adds a participant's wallet address to a draw's participant list.
    This is a more direct way than fetching the whole draw, appending, and saving.
    Ensures participant is not added multiple times if not desired (using $addToSet).
    Args:
        draw_id: The ID of the draw.
        wallet_address: The wallet address of the participant.
    Returns:
        True if participant was added or already existed, False on error or if draw_id invalid.
    """
    try:
        collection = get_draws_collection()
        if not ObjectId.is_valid(draw_id):
            return False

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(draw_id)},
            {"$addToSet": {"participants": wallet_address}} # $addToSet adds only if not already present
        )
        # modified_count will be 0 if participant already exists, which is fine.
        # matched_count will be 1 if draw exists.
        return result.matched_count > 0
    except PyMongoError as e:
        print(f"Error adding participant to draw {draw_id} in MongoDB: {e}")
        return False
