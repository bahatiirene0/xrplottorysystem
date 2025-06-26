from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from .models import (
    AchievementDefinition, UserAchievement, UserLoyalty,
    AchievementDefinitionCreate, AchievementDefinitionUpdate # For type hinting if needed
)

# --- Collection Getters ---
def get_achievement_definitions_collection() -> Collection:
    db = get_db()
    # Potential index: db.achievement_definitions.create_index("name", unique=True)
    # db.achievement_definitions.create_index("is_active")
    return db.achievement_definitions

def get_user_achievements_collection() -> Collection:
    db = get_db()
    # Potential index: db.user_achievements.create_index([("user_wallet_address", 1), ("achievement_definition_id", 1)], unique=True)
    return db.user_achievements

def get_user_loyalty_collection() -> Collection:
    db = get_db()
    # Potential index: db.user_loyalty.create_index("user_wallet_address", unique=True)
    return db.user_loyalty

# --- AchievementDefinition CRUD ---

def create_achievement_definition(definition_data: AchievementDefinitionCreate) -> AchievementDefinition | None:
    try:
        collection = get_achievement_definitions_collection()
        # Pydantic models handle default_factory for created_at, updated_at
        ach_def = AchievementDefinition(**definition_data.model_dump())

        inserted_doc = ach_def.model_dump(by_alias=True, exclude_none=True)
        if "_id" in inserted_doc and inserted_doc["_id"] is None: # Should be handled by model default
            del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        created_def = collection.find_one({"_id": result.inserted_id})
        return AchievementDefinition(**created_def) if created_def else None
    except PyMongoError as e: # Catch duplicate name if unique index exists
        print(f"Error creating achievement definition: {e}")
        return None

def get_achievement_definition_by_id(definition_id: str) -> AchievementDefinition | None:
    try:
        collection = get_achievement_definitions_collection()
        if not ObjectId.is_valid(definition_id): return None
        data = collection.find_one({"_id": ObjectId(definition_id)})
        return AchievementDefinition(**data) if data else None
    except PyMongoError as e:
        print(f"Error getting achievement definition by ID {definition_id}: {e}")
        return None

def get_all_achievement_definitions(active_only: bool = False) -> List[AchievementDefinition]:
    definitions = []
    try:
        collection = get_achievement_definitions_collection()
        query = {}
        if active_only:
            query["is_active"] = True
        results = collection.find(query).sort("name", 1)
        for data in results:
            definitions.append(AchievementDefinition(**data))
        return definitions
    except PyMongoError as e:
        print(f"Error fetching all achievement definitions: {e}")
        return []

def update_achievement_definition(definition_id: str, update_data: AchievementDefinitionUpdate) -> AchievementDefinition | None:
    try:
        collection = get_achievement_definitions_collection()
        if not ObjectId.is_valid(definition_id): return None

        update_fields = update_data.model_dump(exclude_unset=True)
        if not update_fields: # No actual fields to update
            return get_achievement_definition_by_id(definition_id)

        update_fields["updated_at"] = datetime.utcnow()

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(definition_id)},
            {"$set": update_fields}
        )
        if result.modified_count > 0 or result.matched_count > 0 : # Return even if no fields changed but doc matched
            return get_achievement_definition_by_id(definition_id)
        return None
    except PyMongoError as e:
        print(f"Error updating achievement definition {definition_id}: {e}")
        return None

def delete_achievement_definition(definition_id: str) -> bool:
    try:
        collection = get_achievement_definitions_collection()
        if not ObjectId.is_valid(definition_id): return False
        # Consider implications: what if users have earned this achievement?
        # Soft delete (is_active=False) is often better. For now, direct delete.
        result: DeleteResult = collection.delete_one({"_id": ObjectId(definition_id)})
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting achievement definition {definition_id}: {e}")
        return False

# --- UserAchievement Management ---

def grant_achievement_to_user(user_wallet: str, definition: AchievementDefinition) -> UserAchievement | None:
    try:
        collection = get_user_achievements_collection()
        # Check if user already has this achievement
        existing = collection.find_one({
            "user_wallet_address": user_wallet,
            "achievement_definition_id": str(definition.id) # Ensure definition.id is str
        })
        if existing:
            print(f"User {user_wallet} already has achievement {definition.name} (ID: {definition.id}).")
            return UserAchievement(**existing) # Return existing one

        user_ach = UserAchievement(
            user_wallet_address=user_wallet,
            achievement_definition_id=str(definition.id), # Ensure ID is string
            name=definition.name,
            description=definition.description,
            icon_url=definition.icon_url
            # earned_at has default_factory
        )
        inserted_doc = user_ach.model_dump(by_alias=True, exclude_none=True)
        if "_id" in inserted_doc and inserted_doc["_id"] is None:
            del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        created_user_ach = collection.find_one({"_id": result.inserted_id})

        # After granting achievement, update loyalty points if applicable
        if definition.points_reward > 0:
            update_user_loyalty_points(user_wallet, definition.points_reward)

        return UserAchievement(**created_user_ach) if created_user_ach else None
    except DuplicateKeyError: # If unique index on (user_wallet_address, achievement_definition_id) exists
        print(f"DuplicateKeyError: User {user_wallet} likely already granted achievement ID {definition.id} (race condition?).")
        existing = collection.find_one({"user_wallet_address": user_wallet, "achievement_definition_id": str(definition.id)})
        return UserAchievement(**existing) if existing else None
    except PyMongoError as e:
        print(f"Error granting achievement {definition.id} to user {user_wallet}: {e}")
        return None

def get_user_achievements(user_wallet: str) -> List[UserAchievement]:
    achievements = []
    try:
        collection = get_user_achievements_collection()
        results = collection.find({"user_wallet_address": user_wallet}).sort("earned_at", -1)
        for data in results:
            achievements.append(UserAchievement(**data))
        return achievements
    except PyMongoError as e:
        print(f"Error fetching achievements for user {user_wallet}: {e}")
        return []

def check_if_user_has_achievement(user_wallet: str, definition_id: str) -> bool:
    try:
        collection = get_user_achievements_collection()
        if not ObjectId.is_valid(definition_id): return False # Should be str from model
        count = collection.count_documents({"user_wallet_address": user_wallet, "achievement_definition_id": definition_id})
        return count > 0
    except PyMongoError as e:
        print(f"Error checking achievement {definition_id} for user {user_wallet}: {e}")
        return False

# --- UserLoyalty Management ---

def get_or_create_user_loyalty(user_wallet: str) -> UserLoyalty | None:
    try:
        collection = get_user_loyalty_collection()
        loyalty_data = collection.find_one({"user_wallet_address": user_wallet})
        if loyalty_data:
            return UserLoyalty(**loyalty_data)

        # Create new loyalty record
        new_loyalty = UserLoyalty(user_wallet_address=user_wallet, current_points=0)
        inserted_doc = new_loyalty.model_dump(by_alias=True, exclude_none=True)
        # Ensure _id is not in the dict if it's None and aliased
        if "_id" in inserted_doc and inserted_doc["_id"] is None:
           del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        # Set _id for the Pydantic model based on what DB generated, or user_wallet_address if that's the _id strategy
        # If _id is user_wallet_address, then find_one({"_id": user_wallet_address})
        # Assuming default ObjectId for now.
        created_loyalty = collection.find_one({"_id": result.inserted_id})
        return UserLoyalty(**created_loyalty) if created_loyalty else None
    except DuplicateKeyError: # If user_wallet_address is unique index and race condition
        loyalty_data = collection.find_one({"user_wallet_address": user_wallet})
        return UserLoyalty(**loyalty_data) if loyalty_data else None
    except PyMongoError as e:
        print(f"Error getting/creating loyalty for user {user_wallet}: {e}")
        return None

def update_user_loyalty_points(user_wallet: str, points_to_add: int) -> UserLoyalty | None:
    if points_to_add == 0: # No change
        return get_or_create_user_loyalty(user_wallet)
    try:
        collection = get_user_loyalty_collection()
        # Ensure loyalty record exists, then update
        loyalty_record = get_or_create_user_loyalty(user_wallet)
        if not loyalty_record:
            # This implies get_or_create_user_loyalty failed, error already printed.
            return None

        result: UpdateResult = collection.update_one(
            {"user_wallet_address": user_wallet},
            {
                "$inc": {"current_points": points_to_add},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=False # Should not upsert here, get_or_create handles creation
        )
        if result.modified_count > 0 or result.matched_count > 0 :
            return get_or_create_user_loyalty(user_wallet) # Fetch updated record

        # If no modification or match, something is off, as get_or_create should have made one.
        # This path should ideally not be hit if get_or_create_user_loyalty is robust.
        print(f"Loyalty points update for {user_wallet} did not modify/match. Current points: {loyalty_record.current_points if loyalty_record else 'N/A'}")
        return loyalty_record # Return potentially stale record if update failed silently

    except PyMongoError as e:
        print(f"Error updating loyalty points for user {user_wallet}: {e}")
        return None
