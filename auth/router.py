from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # This line might be removable if not used elsewhere directly
import logging

from . import utils as auth_utils
from .models import ChallengeRequest, ChallengeResponse, TokenRequest, TokenResponse, TokenData, auth_config
# TokenData might not be needed here if get_current_user_from_token is the only consumer from this file
from users.db import get_or_create_user # To ensure user exists upon successful login
# from .dependencies import get_current_user_from_token # No longer needed here

router = APIRouter()
logger = logging.getLogger(__name__)

# token_bearer_scheme moved to dependencies.py

@router.post("/challenge", response_model=ChallengeResponse, summary="Request a sign-in challenge")
async def request_challenge(request_data: ChallengeRequest):
    """
    Initiates the login process. A client provides their wallet address,
    and the server returns a unique message that the client must sign.
    """
    wallet_address = request_data.wallet_address
    if not auth_utils.is_valid_xrpl_address(wallet_address):
        logger.warning(f"Invalid XRPL address format for challenge request: {wallet_address}")
        raise HTTPException(status_code=400, detail="Invalid XRPL wallet address format.")

    try:
        # Ensure user record exists or is created before issuing a challenge
        # This helps in associating challenges with known (or newly registered) entities
        user = get_or_create_user(wallet_address)
        if not user:
            logger.error(f"Failed to get or create user for wallet: {wallet_address} before challenge.")
            raise HTTPException(status_code=500, detail="User profile could not be prepared.")

        message_to_sign = auth_utils.generate_challenge_message(wallet_address)
        expires_at = auth_utils.store_challenge(message_to_sign, wallet_address)
        logger.info(f"Challenge requested for {wallet_address}. Message: '{message_to_sign}'")
        return ChallengeResponse(message_to_sign=message_to_sign, expires_at=expires_at.isoformat())
    except Exception as e:
        logger.exception(f"Error during challenge generation for {wallet_address}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate login challenge.")


@router.post("/token", response_model=TokenResponse, summary="Exchange signed challenge for JWT")
async def login_for_access_token(request_data: TokenRequest):
    """
    Client sends their wallet address, the public key used for signing,
    the original challenge message, and the signature.
    If valid, server returns a JWT.
    """
    wallet_address = request_data.wallet_address
    public_key_hex = request_data.public_key_hex
    signature_hex = request_data.signature
    original_message = request_data.challenge_message

    # 1. Validate wallet address format (basic check)
    if not auth_utils.is_valid_xrpl_address(wallet_address):
        logger.warning(f"Invalid XRPL address format for token request: {wallet_address}")
        raise HTTPException(status_code=400, detail="Invalid XRPL wallet address format.")

    # 2. Validate the challenge itself (exists, not expired, matches wallet)
    #    This also invalidates the challenge from the store.
    if not auth_utils.get_and_validate_challenge(original_message, wallet_address):
        logger.warning(f"Challenge validation failed for {wallet_address}. Message: '{original_message}'")
        raise HTTPException(status_code=401, detail="Invalid, expired, or mismatched challenge.")

    # 3. Check if the provided public key corresponds to the wallet address
    #    This is a crucial step to ensure the public key isn't arbitrary.
    if not auth_utils.check_public_key_matches_address(public_key_hex, wallet_address):
        logger.warning(f"Public key {public_key_hex} does not match address {wallet_address}.")
        raise HTTPException(status_code=401, detail="Public key does not correspond to the provided wallet address.")

    # 4. Verify the signature
    is_signature_valid = auth_utils.verify_xrpl_signature(
        public_key_hex=public_key_hex,
        message=original_message,
        signature_hex=signature_hex
    )

    if not is_signature_valid:
        logger.warning(f"Signature verification failed for {wallet_address}.")
        raise HTTPException(status_code=401, detail="Signature verification failed.")

    # 5. Signature is valid. Ensure user exists (should have been handled by challenge phase, but good check)
    user = get_or_create_user(wallet_address)
    if not user:
        logger.error(f"User {wallet_address} not found after successful signature verification.")
        # This should ideally not happen if challenge creation ensures user exists.
        raise HTTPException(status_code=500, detail="User profile not found after authentication.")

    # 6. Create access token
    # The "sub" (subject) of the token should be the wallet_address
    access_token = auth_utils.create_access_token(data={"sub": wallet_address})
    logger.info(f"Access token generated for {wallet_address}.")
    return TokenResponse(access_token=access_token)

# get_current_user_from_token moved to dependencies.py

# Example of a protected route (can be in any other router)
# @router.get("/me", response_model=TokenData) # Assuming TokenData holds what you want to return about user
# async def read_users_me(current_user: TokenData = Depends(get_current_user_from_token)):
# return current_user

# Add this router to app.py
# from auth.router import router as auth_router
# app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
