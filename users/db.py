from pymongo.collection import Collection
from pymongo.results import UpdateResult
from pymongo.errors import PyMongoError
from datetime import datetime
from typing import Optional

from database import get_db
from .models import User, UserCreate # UserCreate might not be directly used if get_or_create handles it

def get_users_collection() -> Collection:
    """Returns the 'users' collection from MongoDB."""
    db = get_db()
    # Ensure indexes - this should ideally be done once at app startup or offline.
    # For example, in your main app startup:
    # with MongoClient(MONGO_URI) as client:
    #     db = client[DB_NAME]
    #     db.users.create_index("wallet_address", unique=True)
    return db.users

def get_user_by_wallet_address(wallet_address: str) -> User | None:
    """Retrieves a user by their wallet address."""
    try:
        collection = get_users_collection()
        user_data = collection.find_one({"wallet_address": wallet_address})
        if user_data:
            return User(**user_data)
        return None
    except PyMongoError as e:
        print(f"Error retrieving user by wallet_address '{wallet_address}': {e}")
        return None
    except Exception as e: # Catch Pydantic validation errors or other issues
        print(f"Error processing data for user wallet_address '{wallet_address}': {e}")
        return None

def get_or_create_user(wallet_address: str) -> User | None:
    """
    Retrieves a user by wallet address or creates a new one if not found.
    This version doesn't take a nickname on creation; nickname is set via update.
    """
    try:
        collection = get_users_collection()
        user = get_user_by_wallet_address(wallet_address)
        if user:
            return user

        # User not found, create a new one
        current_time = datetime.utcnow()
        new_user_data = {
            "wallet_address": wallet_address,
            "nickname": None, # Nickname is explicitly not set on creation here
            "created_at": current_time,
            "updated_at": current_time,
        }
        result = collection.insert_one(new_user_data)
        created_user_doc = collection.find_one({"_id": result.inserted_id})
        if created_user_doc:
            return User(**created_user_doc)
        return None
    except PyMongoError as e: # Handles potential duplicate key error if race condition, though get_user should prevent most
        print(f"PyMongoError in get_or_create_user for wallet '{wallet_address}': {e}")
        # Attempt to fetch again in case of a race condition where another process created it
        user = get_user_by_wallet_address(wallet_address)
        return user
    except Exception as e:
        print(f"Unexpected error in get_or_create_user for wallet '{wallet_address}': {e}")
        return None


def update_user_nickname(wallet_address: str, nickname: Optional[str]) -> User | None:
    """Updates the user's nickname."""
    try:
        collection = get_users_collection()
        update_data = {
            "nickname": nickname,
            "updated_at": datetime.utcnow()
        }
        result: UpdateResult = collection.update_one(
            {"wallet_address": wallet_address},
            {"$set": update_data}
        )
        if result.matched_count > 0:
            return get_user_by_wallet_address(wallet_address)
        return None # User not found or nickname was the same (if modified_count is checked)
    except PyMongoError as e:
        print(f"Error updating nickname for wallet '{wallet_address}': {e}")
        return None
    except Exception as e:
        print(f"Unexpected error updating nickname for wallet '{wallet_address}': {e}")
        return None
