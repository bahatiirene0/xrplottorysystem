from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from . import utils as auth_utils
from .models import TokenData # Assuming TokenData is what get_current_active_user returns
from jose import JWTError # Make sure JWTError is imported from jose

logger = logging.getLogger(__name__)
token_bearer_scheme = HTTPBearer()

async def get_current_user_from_token(
    authorization: HTTPAuthorizationCredentials = Depends(token_bearer_scheme)
) -> TokenData:
    """
    FastAPI dependency to extract and validate token from Authorization header.
    Returns TokenData (containing wallet_address) if valid.
    """
    if authorization is None:
        logger.debug("No authorization credentials provided.")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        token = authorization.credentials
        # get_current_active_user is in auth_utils and expects the token string
        token_data = await auth_utils.get_current_active_user(token)
        return token_data
    except JWTError as e: # Catch specific JWTError from get_current_active_user
        logger.info(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=str(e), # Provide specific error like "Token has expired"
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e: # Catch any other unexpected error during token validation
        logger.exception(f"Unexpected error in get_current_user_from_token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
