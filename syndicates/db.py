from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from .models import (
    Syndicate, SyndicateMember, SyndicateMemberStatus,
    SyndicateTicketPurchase, SyndicateWinningsDistribution, MemberShare
)
from users.db import get_user_by_wallet_address # To fetch nickname

def get_syndicates_collection() -> Collection:
    db = get_db()
    # Potential indexes:
    # db.syndicates.create_index("creator_wallet_address")
    # db.syndicates.create_index("members.wallet_address") # For finding syndicates a user is in
    return db.syndicates

def get_syndicate_ticket_purchases_collection() -> Collection:
    db = get_db()
    # Potential indexes:
    # db.syndicate_ticket_purchases.create_index("syndicate_id")
    # db.syndicate_ticket_purchases.create_index("draw_id")
    # db.syndicate_ticket_purchases.create_index("ticket_ids") # If querying by specific ticket
    return db.syndicate_ticket_purchases

def get_syndicate_winnings_collection() -> Collection:
    db = get_db()
    # Potential indexes:
    # db.syndicate_winnings.create_index("syndicate_id")
    # db.syndicate_winnings.create_index("draw_id")
    # db.syndicate_winnings.create_index("winning_ticket_id")
    return db.syndicate_winnings

# --- Syndicate CRUD ---

def create_syndicate(name: str, description: Optional[str], creator_wallet_address: str, default_category_id: Optional[str]) -> Syndicate | None:
    try:
        collection = get_syndicates_collection()
        creator_user_profile = get_user_by_wallet_address(creator_wallet_address)
        creator_nickname = creator_user_profile.nickname if creator_user_profile else None

        initial_member = SyndicateMember(
            wallet_address=creator_wallet_address,
            nickname=creator_nickname,
            join_date=datetime.utcnow(),
            status=SyndicateMemberStatus.ACTIVE # Creator is active by default
        )
        syndicate_data = Syndicate(
            name=name,
            description=description,
            creator_wallet_address=creator_wallet_address,
            members=[initial_member],
            default_lottery_category_id=default_category_id,
            # created_at, updated_at have default_factory
        )

        inserted_doc = syndicate_data.model_dump(by_alias=True, exclude_none=True)
        # `id` with `default=None` and `alias='_id'` should not be in `inserted_doc` if None
        if "_id" in inserted_doc and inserted_doc["_id"] is None:
            del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        created_syndicate = collection.find_one({"_id": result.inserted_id})
        return Syndicate(**created_syndicate) if created_syndicate else None
    except PyMongoError as e:
        print(f"Error creating syndicate: {e}")
        return None

def get_syndicate_by_id(syndicate_id: str) -> Syndicate | None:
    try:
        collection = get_syndicates_collection()
        if not ObjectId.is_valid(syndicate_id): return None
        data = collection.find_one({"_id": ObjectId(syndicate_id)})
        return Syndicate(**data) if data else None
    except PyMongoError as e:
        print(f"Error getting syndicate by ID {syndicate_id}: {e}")
        return None

def update_syndicate_details(syndicate_id: str, name: Optional[str], description: Optional[str], default_category_id: Optional[str]) -> Syndicate | None:
    try:
        collection = get_syndicates_collection()
        if not ObjectId.is_valid(syndicate_id): return None

        update_fields = {"updated_at": datetime.utcnow()}
        if name is not None: update_fields["name"] = name
        if description is not None: update_fields["description"] = description
        if default_category_id is not None: update_fields["default_lottery_category_id"] = default_category_id

        result: UpdateResult = collection.update_one(
            {"_id": ObjectId(syndicate_id)},
            {"$set": update_fields}
        )
        if result.modified_count > 0:
            return get_syndicate_by_id(syndicate_id)
        # If nothing changed but syndicate exists, could return current state or None/False
        current_syndicate = get_syndicate_by_id(syndicate_id)
        if current_syndicate and result.matched_count > 0 : return current_syndicate # No change but found
        return None

    except PyMongoError as e:
        print(f"Error updating syndicate {syndicate_id}: {e}")
        return None

def delete_syndicate_by_id(syndicate_id: str) -> bool:
    try:
        collection = get_syndicates_collection()
        if not ObjectId.is_valid(syndicate_id): return False
        # Consider implications: what if syndicate has active participations or pending winnings?
        # For now, direct delete. Add checks or soft delete if needed.
        result: DeleteResult = collection.delete_one({"_id": ObjectId(syndicate_id)})
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error deleting syndicate {syndicate_id}: {e}")
        return False

def get_syndicates_for_member(wallet_address: str) -> List[Syndicate]:
    syndicates = []
    try:
        collection = get_syndicates_collection()
        # Find syndicates where the members array contains an element matching the wallet_address and status is active or invited
        query = {"members": {"$elemMatch": {"wallet_address": wallet_address, "status": {"$in": [SyndicateMemberStatus.ACTIVE, SyndicateMemberStatus.INVITED]}}}}
        # Also include syndicates created by the user
        # query = {"$or": [
        #     {"creator_wallet_address": wallet_address},
        #     {"members": {"$elemMatch": {"wallet_address": wallet_address, "status": {"$in": [SyndicateMemberStatus.ACTIVE, SyndicateMemberStatus.INVITED]}}}}
        # ]}
        # Simpler: just based on membership for "my_syndicates" for now

        results = collection.find(query)
        for data in results:
            syndicates.append(Syndicate(**data))
        return syndicates
    except PyMongoError as e:
        print(f"Error fetching syndicates for member {wallet_address}: {e}")
        return []

# --- Syndicate Member Management ---

def add_or_update_syndicate_member(syndicate_id: str, member_wallet: str, status: SyndicateMemberStatus, invited_by_wallet: Optional[str] = None) -> Syndicate | None:
    try:
        collection = get_syndicates_collection()
        if not ObjectId.is_valid(syndicate_id): return None

        syndicate = get_syndicate_by_id(syndicate_id)
        if not syndicate: return None

        member_idx = -1
        for i, mem in enumerate(syndicate.members):
            if mem.wallet_address == member_wallet:
                member_idx = i
                break

        user_profile = get_user_by_wallet_address(member_wallet)
        nickname = user_profile.nickname if user_profile else None

        if member_idx != -1: # Update existing member
            update_query = {f"members.{member_idx}.status": status.value, "updated_at": datetime.utcnow()}
            if status == SyndicateMemberStatus.ACTIVE and syndicate.members[member_idx].status == SyndicateMemberStatus.INVITED:
                update_query[f"members.{member_idx}.join_date"] = datetime.utcnow()
            if nickname is not None: # Update nickname if fetched
                 update_query[f"members.{member_idx}.nickname"] = nickname

            collection.update_one({"_id": ObjectId(syndicate_id)}, {"$set": update_query})
        else: # Add new member (typically for invite)
            if status != SyndicateMemberStatus.INVITED: # Only allow adding new members as 'invited' initially by this function path
                 print(f"Cannot add new member {member_wallet} to syndicate {syndicate_id} with status {status}. Must be invited first.")
                 return None # Or raise error

            new_member = SyndicateMember(wallet_address=member_wallet, nickname=nickname, status=SyndicateMemberStatus.INVITED)
            collection.update_one(
                {"_id": ObjectId(syndicate_id)},
                {"$push": {"members": new_member.model_dump()}, "$set": {"updated_at": datetime.utcnow()}}
            )
        return get_syndicate_by_id(syndicate_id)
    except PyMongoError as e:
        print(f"Error adding/updating member {member_wallet} in syndicate {syndicate_id}: {e}")
        return None

def remove_syndicate_member(syndicate_id: str, member_wallet: str, new_status: SyndicateMemberStatus = SyndicateMemberStatus.REMOVED) -> Syndicate | None:
    """ Can be used for 'leave' (status=LEFT) or 'remove' (status=REMOVED) """
    try:
        collection = get_syndicates_collection()
        if not ObjectId.is_valid(syndicate_id): return None

        syndicate = get_syndicate_by_id(syndicate_id)
        if not syndicate or not any(m.wallet_address == member_wallet for m in syndicate.members):
            return None # Syndicate or member not found

        # Instead of $pull, update status to LEFT or REMOVED to keep history if desired.
        # Or, if true removal:
        # result = collection.update_one(
        #     {"_id": ObjectId(syndicate_id)},
        #     {"$pull": {"members": {"wallet_address": member_wallet}}, "$set": {"updated_at": datetime.utcnow()}}
        # )
        # For now, update status:
        res = collection.update_one(
            {"_id": ObjectId(syndicate_id), "members.wallet_address": member_wallet},
            {"$set": {"members.$.status": new_status.value, "updated_at": datetime.utcnow()}}
        )
        if res.modified_count == 0 and res.matched_count == 0: # Defensive check
            print(f"Member {member_wallet} not found or status not changed in syndicate {syndicate_id}")
            return None

        return get_syndicate_by_id(syndicate_id)
    except PyMongoError as e:
        print(f"Error removing member {member_wallet} from syndicate {syndicate_id}: {e}")
        return None

# --- Syndicate Participation & Winnings ---

def record_syndicate_ticket_purchase(syndicate_id: str, draw_id: str, purchased_by_wallet: str, ticket_ids: List[str]) -> SyndicateTicketPurchase | None:
    try:
        collection = get_syndicate_ticket_purchases_collection()
        purchase_data = SyndicateTicketPurchase(
            syndicate_id=syndicate_id,
            draw_id=draw_id,
            purchased_by_wallet_address=purchased_by_wallet,
            ticket_ids=ticket_ids
            # purchase_timestamp has default_factory
        )
        inserted_doc = purchase_data.model_dump(by_alias=True, exclude_none=True)
        if "_id" in inserted_doc and inserted_doc["_id"] is None:
            del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        created_purchase = collection.find_one({"_id": result.inserted_id})
        return SyndicateTicketPurchase(**created_purchase) if created_purchase else None
    except PyMongoError as e:
        print(f"Error recording syndicate ticket purchase for syndicate {syndicate_id}, draw {draw_id}: {e}")
        return None

def get_syndicate_purchase_for_ticket(ticket_id: str, draw_id: str) -> SyndicateTicketPurchase | None:
    try:
        collection = get_syndicate_ticket_purchases_collection()
        # Find a purchase record that includes this ticket_id for the given draw_id
        data = collection.find_one({"draw_id": draw_id, "ticket_ids": ticket_id})
        return SyndicateTicketPurchase(**data) if data else None
    except PyMongoError as e:
        print(f"Error finding syndicate purchase for ticket {ticket_id}, draw {draw_id}: {e}")
        return None

def record_syndicate_winnings(
    syndicate_id: str,
    draw_id: str,
    winning_ticket_id: str,
    total_gross: float,
    fee_charged: float,
    total_net: float,
    member_distributions: List[MemberShare]
) -> SyndicateWinningsDistribution | None:
    try:
        collection = get_syndicate_winnings_collection()
        winnings_data = SyndicateWinningsDistribution(
            syndicate_id=syndicate_id,
            draw_id=draw_id,
            winning_ticket_id=winning_ticket_id,
            total_syndicate_prize_gross=total_gross,
            platform_fee_charged=fee_charged,
            total_syndicate_prize_net=total_net,
            member_distributions=member_distributions
            # distribution_timestamp has default_factory
        )
        inserted_doc = winnings_data.model_dump(by_alias=True, exclude_none=True)
        if "_id" in inserted_doc and inserted_doc["_id"] is None:
            del inserted_doc["_id"]

        result: InsertOneResult = collection.insert_one(inserted_doc)
        created_winnings = collection.find_one({"_id": result.inserted_id})
        return SyndicateWinningsDistribution(**created_winnings) if created_winnings else None
    except PyMongoError as e:
        print(f"Error recording syndicate winnings for syndicate {syndicate_id}, draw {draw_id}: {e}")
        return None

def get_syndicate_winnings_for_draw(syndicate_id: str, draw_id: str) -> List[SyndicateWinningsDistribution]:
    winnings_list = []
    try:
        collection = get_syndicate_winnings_collection()
        results = collection.find({"syndicate_id": syndicate_id, "draw_id": draw_id})
        for data in results:
            winnings_list.append(SyndicateWinningsDistribution(**data))
        return winnings_list
    except PyMongoError as e:
        print(f"Error fetching syndicate winnings for syndicate {syndicate_id}, draw {draw_id}: {e}")
        return []
