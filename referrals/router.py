from fastapi import APIRouter, HTTPException, Body, Depends, Path, Query
from typing import List, Optional

from . import db as referrals_db
from .models import ReferralCode, ReferralLink, UserReferralStats, MyReferralCodeResponse
from pymongo.errors import PyMongoError

router = APIRouter()

class WalletAddressBody(BaseModel): # Pydantic model for request body
    wallet_address: str

@router.post("/code", response_model=MyReferralCodeResponse, status_code=200, summary="Get or Create Referral Code for a Wallet")
async def get_or_create_referral_code_for_wallet(data: WalletAddressBody):
    """
    Retrieves an existing referral code for the provided wallet_address,
    or creates a new one if it doesn't exist.
    Simulates an authenticated user action where wallet_address is trusted.
    """
    try:
        # This simulates "get or create" logic
        existing_code = referrals_db.get_referral_code_by_wallet(data.wallet_address)
        if existing_code:
            return MyReferralCodeResponse(**existing_code.model_dump()) # Use the specific response model

        # If no code exists, create one
        new_code = referrals_db.create_referral_code(data.wallet_address)
        if not new_code:
            raise HTTPException(status_code=500, detail="Failed to create referral code.")
        return MyReferralCodeResponse(**new_code.model_dump())

    except PyMongoError as e:
        print(f"PyMongoError in /code endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error while processing referral code.")
    except Exception as e:
        print(f"Unexpected error in /code endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/stats/{wallet_address}", response_model=UserReferralStats, summary="Get Referral Statistics for a Wallet")
async def get_referral_stats_for_wallet(
    wallet_address: str = Path(..., description="The wallet address to fetch referral stats for.")
):
    """
    Retrieves referral statistics for the given wallet_address.
    This includes their own referral code (if any) and a count of successful referrals.
    """
    try:
        user_code: Optional[ReferralCode] = referrals_db.get_referral_code_by_wallet(wallet_address)

        # Count successful referrals (e.g., those who completed a purchase or a specific action)
        # This requires defining what a "successful" referral means in terms of ReferralLink.reward_status
        # For now, let's count links where reward_status is 'eligible_for_reward' or 'reward_credited'
        successful_referral_links = []
        if user_code: # Only count if they have a code to refer with
            links_by_user_code = await get_links_for_code(user_code.code) # Helper needed or direct query

            # This part needs a db function like get_referral_links_by_code_and_status
            # For simplicity now, let's assume we get all links by referrer and filter
            # This is inefficient for many links.
            all_referrer_links = referrals_db.get_referral_links_by_referrer(wallet_address)
            for link in all_referrer_links:
                if link.reward_status in ["eligible_for_reward", "reward_credited"]:
                    successful_referral_links.append(link)

        # Check if this user was referred by someone
        link_as_referee = referrals_db.get_referral_link_by_referee(wallet_address)
        referred_by_wallet = link_as_referee.referrer_wallet_address if link_as_referee else None

        return UserReferralStats(
            wallet_address=wallet_address,
            referral_code=user_code.code if user_code else None,
            referral_code_usage_count=user_code.usage_count if user_code else 0,
            successful_referrals_count=len(successful_referral_links),
            referred_by=referred_by_wallet
        )

    except PyMongoError as e:
        print(f"PyMongoError in /stats/{wallet_address} endpoint: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching referral stats.")
    except Exception as e:
        print(f"Unexpected error in /stats/{wallet_address} endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Helper function (could be in db.py or here if specific to router logic)
# This is an example, the actual query might be more complex or better placed in db.py
async def get_links_for_code(referral_code: str) -> List[ReferralLink]:
    # This is a placeholder. A proper db function would be:
    # referrals_db.get_referral_links_by_code(referral_code)
    # For now, this won't work as intended without that db function.
    # The current get_referral_links_by_referrer is what's used above.
    # This function is not directly used by the current stats endpoint logic above.
    # It's here to illustrate a potential need.
    print(f"Placeholder: Would fetch links for code {referral_code}")
    return []

# TODO for /stats endpoint:
# The current way of calculating successful_referrals_count by fetching all links by referrer
# and then filtering is not optimal.
# Ideally, add a DB function:
# `count_successful_referrals_for_referrer(referrer_wallet: str, success_statuses: List[str]) -> int`
# For now, the current implementation will work for small numbers but should be optimized.
