import string
import random
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from database import get_db
from .models import ReferralCode, ReferralCodeCreate, ReferralCodeUpdate, \
                    ReferralLink, ReferralLinkCreate, ReferralLinkUpdate

REFERRAL_CODE_LENGTH = 8 # Length of the generated referral code

def get_referral_codes_collection() -> Collection:
    """Returns the 'referral_codes' collection from MongoDB."""
    db = get_db()
    # Ensure indexes - this should ideally be done once at app startup or offline
    # For simplicity, doing it here, but it's not efficient to call repeatedly.
    # In a production app, manage indexes separately.
    # db.referral_codes.create_index("code", unique=True)
    # db.referral_codes.create_index("wallet_address", unique=True) # A user has one code
    return db.referral_codes

def get_referral_links_collection() -> Collection:
    """Returns the 'referral_links' collection from MongoDB."""
    db = get_db()
    # db.referral_links.create_index("referee_wallet_address", unique=True) # A user can be referred once
    # db.referral_links.create_index("referrer_wallet_address")
    return db.referral_links

def generate_unique_referral_code_str(length: int = REFERRAL_CODE_LENGTH) -> str:
    """Generates a random alphanumeric string for a referral code."""
    # Not guaranteed unique globally by itself, uniqueness is enforced by DB insert attempt.
    # For higher volume, might need a more robust unique ID generator or retry loop.
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def create_referral_code(wallet_address: str) -> ReferralCode | None:
    """
    Creates a new referral code for a wallet if one doesn't exist, or returns the existing one.
    A wallet can only have one referral code.
    """
    collection = get_referral_codes_collection()
    try:
        existing_code = collection.find_one({"wallet_address": wallet_address})
        if existing_code:
            return ReferralCode(**existing_code)

        # Try to generate a unique code. Retry a few times if collision (unlikely with reasonable length).
        unique_code_str = ""
        max_retries = 5
        for _ in range(max_retries):
            code_str_candidate = generate_unique_referral_code_str()
            if not collection.find_one({"code": code_str_candidate}):
                unique_code_str = code_str_candidate
                break

        if not unique_code_str:
            print(f"Failed to generate a unique referral code string after {max_retries} retries.")
            return None # Could not generate a unique code

        code_data = ReferralCodeCreate(
            code=unique_code_str,
            wallet_address=wallet_address
            # usage_count and is_active default in ReferralCodeBase/Create
            # created_at, updated_at default in ReferralCodeCreate
        )
        # Pydantic model_dump for v2, .dict() for v1
        data_to_insert = code_data.model_dump()

        result: InsertOneResult = collection.insert_one(data_to_insert)
        created_doc = collection.find_one({"_id": result.inserted_id})
        if created_doc:
            return ReferralCode(**created_doc)
        return None
    except DuplicateKeyError: # Should be caught by the find_one for wallet_address
        print(f"DuplicateKeyError: Referral code likely already exists for wallet {wallet_address} or code collision.")
        existing_code = collection.find_one({"wallet_address": wallet_address})
        if existing_code:
            return ReferralCode(**existing_code)
        return None # Should not happen if wallet_address index is unique
    except PyMongoError as e:
        print(f"Error creating referral code for wallet {wallet_address}: {e}")
        return None


def get_referral_code_by_code(code: str) -> ReferralCode | None:
    """Retrieves a referral code by the code string."""
    try:
        collection = get_referral_codes_collection()
        db_code = collection.find_one({"code": code})
        if db_code:
            return ReferralCode(**db_code)
        return None
    except PyMongoError as e:
        print(f"Error retrieving referral code by code '{code}': {e}")
        return None

def get_referral_code_by_wallet(wallet_address: str) -> ReferralCode | None:
    """Retrieves a referral code by the owner's wallet address."""
    try:
        collection = get_referral_codes_collection()
        db_code = collection.find_one({"wallet_address": wallet_address})
        if db_code:
            return ReferralCode(**db_code)
        return None
    except PyMongoError as e:
        print(f"Error retrieving referral code by wallet '{wallet_address}': {e}")
        return None

def increment_referral_code_usage(code_id_str: str) -> bool:
    """Increments the usage_count of a referral code."""
    try:
        collection = get_referral_codes_collection()
        if not ObjectId.is_valid(code_id_str):
            return False

        code_id = ObjectId(code_id_str)
        result: UpdateResult = collection.update_one(
            {"_id": code_id},
            {
                "$inc": {"usage_count": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error incrementing usage for referral code ID '{code_id_str}': {e}")
        return False

def create_referral_link(referrer_wallet: str, referee_wallet: str, referral_code_used: str) -> ReferralLink | None:
    """
    Creates a referral link if the referee hasn't been referred before.
    """
    collection = get_referral_links_collection()
    try:
        # Check if referee already has a link
        existing_link = collection.find_one({"referee_wallet_address": referee_wallet})
        if existing_link:
            print(f"Referee {referee_wallet} has already been referred.")
            return None # Or return existing_link if that's desired behavior

        link_data = ReferralLinkCreate(
            referrer_wallet_address=referrer_wallet,
            referee_wallet_address=referee_wallet,
            referral_code_used=referral_code_used
            # reward_status defaults in model
            # created_at, updated_at default in model
        )
        data_to_insert = link_data.model_dump()

        result: InsertOneResult = collection.insert_one(data_to_insert)
        created_doc = collection.find_one({"_id": result.inserted_id})
        if created_doc:
            return ReferralLink(**created_doc)
        return None
    except DuplicateKeyError: # This would happen if referee_wallet_address has a unique index
        print(f"DuplicateKeyError: Referral link for referee {referee_wallet} likely already exists.")
        return None # Referee already referred
    except PyMongoError as e:
        print(f"Error creating referral link for referee {referee_wallet} by {referrer_wallet}: {e}")
        return None

def get_referral_link_by_referee(referee_wallet: str) -> ReferralLink | None:
    """Retrieves a referral link by the referee's wallet address."""
    try:
        collection = get_referral_links_collection()
        db_link = collection.find_one({"referee_wallet_address": referee_wallet})
        if db_link:
            return ReferralLink(**db_link)
        return None
    except PyMongoError as e:
        print(f"Error retrieving referral link by referee '{referee_wallet}': {e}")
        return None

def get_referral_links_by_referrer(referrer_wallet: str, limit: int = 50, offset: int = 0) -> List[ReferralLink]:
    """Retrieves all referral links initiated by a specific referrer, with pagination."""
    links = []
    try:
        collection = get_referral_links_collection()
        db_links = collection.find({"referrer_wallet_address": referrer_wallet}).sort("created_at", -1).skip(offset).limit(limit)
        for link_data in db_links:
            links.append(ReferralLink(**link_data))
        return links
    except PyMongoError as e:
        print(f"Error retrieving referral links by referrer '{referrer_wallet}': {e}")
        return []

def update_referral_link_status(link_id_str: str, new_status: str) -> bool:
    """Updates the reward_status of a referral link."""
    try:
        collection = get_referral_links_collection()
        if not ObjectId.is_valid(link_id_str):
            return False

        link_id = ObjectId(link_id_str)
        update_data = ReferralLinkUpdate(reward_status=new_status, updated_at=datetime.utcnow())

        result: UpdateResult = collection.update_one(
            {"_id": link_id},
            {"$set": update_data.model_dump(exclude_unset=True)}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error updating status for referral link ID '{link_id_str}': {e}")
        return False

# Note on Indexes:
# For 'referral_codes':
# - Create unique index on 'code'
# - Create unique index on 'wallet_address' (if one user gets one code)
# For 'referral_links':
# - Create unique index on 'referee_wallet_address'
# - Create index on 'referrer_wallet_address'
# These should be created once, e.g., via an admin script or on app startup using PyMongo's `create_indexes`.
# Example (do this in database.py or a setup script):
# def setup_referral_indexes(db_client):
#     codes_collection = db_client[DB_NAME].referral_codes
#     codes_collection.create_index("code", unique=True)
#     codes_collection.create_index("wallet_address", unique=True)
#
#     links_collection = db_client[DB_NAME].referral_links
#     links_collection.create_index("referee_wallet_address", unique=True)
#     links_collection.create_index("referrer_wallet_address")
# This is commented out here as db.py is for functions, not index setup directly.
# The index hints in models.py `Field(..., index=True)` are for documentation/ORM use,
# Pydantic itself doesn't create DB indexes.
# `unique=True` in `Field` is also for documentation for basic Pydantic,
# actual DB unique constraint is via `create_index`.
# For `referee_wallet_address`, the `DuplicateKeyError` handling relies on this unique index.
# For `code` and `wallet_address` in `referral_codes`, the `create_referral_code` has a find-first logic
# to handle "get or create" and a retry for code string generation, but unique indexes are still best practice.
