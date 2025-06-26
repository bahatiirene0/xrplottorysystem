from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional

from . import db as users_db
from .models import User, UserUpdate
from auth.dependencies import get_current_user_from_token # Import the real dependency
from auth.models import TokenData # To type hint the dependency result

router = APIRouter()

# Placeholder get_current_user_wallet_address removed.

@router.post("/profile", response_model=User, summary="Set or Update User Nickname")
async def set_or_update_user_profile(
    user_update: UserUpdate,
    token_data: TokenData = Depends(get_current_user_from_token) # Use the real dependency
):
    """
    Allows an authenticated user to set or update their nickname.
    The user is identified by their wallet address from the auth token.
    """
    current_wallet_address = token_data.wallet_address
    if not current_wallet_address:
        # This should not happen if token_data is correctly populated by get_current_user_from_token
        raise HTTPException(status_code=401, detail="Could not identify user from token.")
    try:
        # Ensure user exists
        user = users_db.get_or_create_user(current_wallet_address)
        if not user:
            raise HTTPException(status_code=404, detail="User not found, though should have been created/retrieved.")

        updated_user = users_db.update_user_nickname(current_wallet_address, user_update.nickname)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update user nickname.")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/profile", response_model=User, summary="Get User Profile")
async def get_user_profile(
    token_data: TokenData = Depends(get_current_user_from_token) # Use the real dependency
):
    """
    Allows an authenticated user to retrieve their profile information
    (wallet address and nickname).
    """
    current_wallet_address = token_data.wallet_address
    if not current_wallet_address:
        raise HTTPException(status_code=401, detail="Could not identify user from token.")
    try:
        user = users_db.get_or_create_user(current_wallet_address) # Ensures user exists
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found or could not be created.")
        return user
    except HTTPException:
        raise
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# The user module should be included in the main app.py
# Example for app.py:
# from users.router import router as users_router
# app.include_router(users_router, prefix="/api/users", tags=["Users"])
