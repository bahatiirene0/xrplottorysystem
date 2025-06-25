from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import get_db
from .models import Draw, DrawCreate, DrawUpdate

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
        current_time = datetime.utcnow()
        # Use model_dump for Pydantic v2, dict() for v1
        data_to_insert = draw_data.model_dump()
        data_to_insert["created_at"] = current_time
        data_to_insert["updated_at"] = current_time
        # Ensure participants list exists if not provided, though model has default_factory
        if "participants" not in data_to_insert:
            data_to_insert["participants"] = []

        result: InsertOneResult = collection.insert_one(data_to_insert)
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
            return None
        db_draw = collection.find_one({"_id": ObjectId(draw_id)})
        if db_draw:
            return Draw(**db_draw) # Pydantic handles _id alias
        return None
    except PyMongoError as e:
        print(f"Error retrieving draw by ID '{draw_id}' from MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error processing data for draw ID '{draw_id}': {e}")
        return None

def get_open_draws_for_category(category_id: str) -> List[Draw]:
    """
    Retrieves all draws with status 'open' for a specific category,
    ordered by scheduled_close_time ascending (soonest to close first).
    """
    draws = []
    try:
        collection = get_draws_collection()
        now = datetime.utcnow()
        # Find draws that are 'open' and their scheduled_close_time is in the future
        # and their scheduled_open_time is in the past (or now)
        query = {
            "category_id": category_id,
            "status": "open",
            "scheduled_open_time": {"$lte": now},
            "scheduled_close_time": {"$gt": now}
        }
        db_draws = collection.find(query).sort("scheduled_close_time", 1)
        for d_data in db_draws:
            try:
                draws.append(Draw(**d_data))
            except Exception as e:
                print(f"Error processing open draw data for _id '{d_data.get('_id')}': {e}")
                continue
        return draws
    except PyMongoError as e:
        print(f"Error retrieving open draws for category '{category_id}' from MongoDB: {e}")
        return []

def get_next_pending_draw(category_id: Optional[str] = None) -> Draw | None:
    """
    Retrieves the next draw with status 'pending_open', ordered by scheduled_open_time.
    Optionally filters by category_id.
    """
    try:
        collection = get_draws_collection()
        query: Dict[str, Any] = {"status": "pending_open"}
        if category_id:
            if not ObjectId.is_valid(category_id): # Basic check, though category_id is str
                 print(f"Invalid category_id format: {category_id}")
                 return None
            query["category_id"] = category_id

        # Find the one scheduled to open soonest
        db_draw = collection.find_one(query, sort=[("scheduled_open_time", 1)])
        if db_draw:
            return Draw(**db_draw)
        return None
    except PyMongoError as e:
        print(f"Error retrieving next pending draw from MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error processing next pending draw data: {e}")
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

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return True # Nothing to update

        update_dict["updated_at"] = datetime.utcnow()

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(draw_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating draw ID '{draw_id}' in MongoDB: {e}")
        return False

def get_draw_history(category_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> list[Draw]:
    """
    Retrieves draws, ordered by scheduled_close_time descending.
    Optionally filters by category_id. Supports pagination.
    """
    draws = []
    try:
        collection = get_draws_collection()
        query: Dict[str, Any] = {}
        if category_id:
            query["category_id"] = category_id

        # Sort by scheduled_close_time descending to get most recently closed/active first
        db_draws = collection.find(query).sort("scheduled_close_time", -1).skip(offset).limit(limit)
        for d_data in db_draws:
            try:
                draws.append(Draw(**d_data))
            except Exception as e:
                 print(f"Error processing draw history data for _id '{d_data.get('_id')}': {e}")
                 continue
        return draws
    except PyMongoError as e:
        print(f"Error retrieving draw history from MongoDB: {e}")
        return []

# get_participants_for_draw and add_participant_to_draw remain largely the same
# but ensure they use the updated Draw model if fetching the draw object.
# add_participant_to_draw is fine as it directly updates MongoDB.

def get_participants_for_draw(draw_id: str) -> List[str] | None:
    """
    Retrieves the list of participant wallet addresses for a specific draw.
    (This function might be less used if participants are fetched from tickets collection directly)
    """
    try:
        draw = get_draw_by_id(draw_id) # Uses updated Draw model
        if draw:
            return draw.participants
        return None
    except PyMongoError as e: # Should be caught by get_draw_by_id
        print(f"Error retrieving participants for draw {draw_id}: {e}")
        return None

def add_participant_to_draw(draw_id: str, wallet_address: str) -> bool:
    """
    Adds a participant's wallet address to a draw's participant list using $addToSet.
    Also updates the 'updated_at' timestamp for the draw.
    """
    try:
        collection = get_draws_collection()
        if not ObjectId.is_valid(draw_id):
            return False

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(draw_id)},
            {
                "$addToSet": {"participants": wallet_address},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.matched_count > 0 # matched_count is 1 if found, modified_count might be 0 if participant existed
    except PyMongoError as e:
        print(f"Error adding participant to draw {draw_id} in MongoDB: {e}")
        return False
