from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import get_db
from .models import LotteryCategory, LotteryCategoryCreate, LotteryCategoryUpdate

def get_categories_collection() -> Collection:
    """Returns the 'lottery_categories' collection from MongoDB."""
    db = get_db()
    return db.lottery_categories

def create_category(category_data: LotteryCategoryCreate) -> str | None:
    """
    Creates a new lottery category in the database.
    """
    try:
        collection = get_categories_collection()
        current_time = datetime.utcnow()
        # Use model_dump for Pydantic v2, dict() for v1
        data_to_insert = category_data.model_dump()
        data_to_insert["created_at"] = current_time
        data_to_insert["updated_at"] = current_time

        result: InsertOneResult = collection.insert_one(data_to_insert)
        return str(result.inserted_id)
    except PyMongoError as e:
        print(f"Error creating lottery category in MongoDB: {e}")
        return None

def get_category_by_id(category_id: str) -> LotteryCategory | None:
    """
    Retrieves a single lottery category by its ID.
    """
    try:
        collection = get_categories_collection()
        if not ObjectId.is_valid(category_id):
            return None
        db_category = collection.find_one({"_id": ObjectId(category_id)})
        if db_category:
            return LotteryCategory(**db_category) # Pydantic will handle _id alias
        return None
    except PyMongoError as e:
        print(f"Error retrieving lottery category by ID '{category_id}' from MongoDB: {e}")
        return None
    except Exception as e: # Catch Pydantic validation errors or other issues
        print(f"Error processing data for category ID '{category_id}': {e}")
        return None


def get_all_categories(active_only: bool = False) -> list[LotteryCategory]:
    """
    Retrieves all lottery categories, optionally filtering for active ones.
    """
    categories = []
    try:
        collection = get_categories_collection()
        query = {}
        if active_only:
            query["is_active"] = True

        db_categories = collection.find(query).sort("name", 1) # Sort by name
        for cat_data in db_categories:
            try:
                categories.append(LotteryCategory(**cat_data))
            except Exception as e: # Pydantic validation error for a specific doc
                print(f"Error processing category data for _id '{cat_data.get('_id')}': {e}")
                continue # Skip this document
        return categories
    except PyMongoError as e:
        print(f"Error retrieving all lottery categories from MongoDB: {e}")
        return []


def update_category(category_id: str, update_data: LotteryCategoryUpdate) -> bool:
    """
    Updates a lottery category in the database.
    """
    try:
        collection = get_categories_collection()
        if not ObjectId.is_valid(category_id):
            return False

        # model_dump with exclude_unset=True ensures only provided fields are updated
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return True # Nothing to update

        update_dict["updated_at"] = datetime.utcnow()

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating lottery category ID '{category_id}' in MongoDB: {e}")
        return False

def delete_category(category_id: str) -> bool:
    """
    Deletes a lottery category from the database.
    """
    try:
        collection = get_categories_collection()
        if not ObjectId.is_valid(category_id):
            return False
        result: DeleteResult = collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting lottery category ID '{category_id}' from MongoDB: {e}")
        return False
