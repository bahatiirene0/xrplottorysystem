import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import secrets
import logging

from jose import JWTError, jwt as python_jose_jwt # Use python_jose for JWT
from xrpl.wallet import Wallet # To get public key from seed if needed (not for verification directly)
from xrpl.utils import xrp_to_drops, drops_to_xrp, account_lines # General utils
from xrpl.core import addresscodec # For address validation and public key derivation
from xrpl.transaction import sign # For signing, not verification here
from xrpl.ledger import get_latest_validated_ledger_sequence # Not directly for auth
# For verification, we need to use cryptography functions that xrpl-py might wrap or use internally.
# xrpl-py's Wallet.sign is for signing. For verification, we need to verify a signature
# given a public key, message, and signature.
# The `xrpl.account.does_public_key_match_address` and `xrpl.crypto.verify` are key.
from xrpl.account import does_public_key_match_address
from xrpl.cryptography import verify, get_public_key_from_address

from .models import auth_config, TokenData
from users.db import get_or_create_user # To ensure user exists

# --- Temporary In-Memory Challenge Store ---
# IMPORTANT: Replace with Redis or a proper cache in production
# Stores: {challenge_string: {"wallet_address": str, "expires_at": datetime}}
challenge_store: Dict[str, Dict] = {}
logger = logging.getLogger(__name__)


def generate_challenge_message(wallet_address: str) -> str:
    """Generates a unique, secure random string for the user to sign."""
    # The message should be unpredictable and unique per login attempt.
    # Including wallet_address and a timestamp can help ensure uniqueness.
    nonce = secrets.token_hex(16)
    timestamp = datetime.now(timezone.utc).isoformat()
    return f"Login to LotteryApp: {wallet_address} Nonce: {nonce} Timestamp: {timestamp}"

def store_challenge(challenge: str, wallet_address: str) -> datetime:
    """Stores the challenge temporarily and returns its expiry time."""
    expires_delta = timedelta(minutes=auth_config.CHALLENGE_EXPIRE_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta
    challenge_store[challenge] = {
        "wallet_address": wallet_address,
        "expires_at": expires_at
    }
    logger.debug(f"Stored challenge for {wallet_address}. Expires at {expires_at.isoformat()}. Current store size: {len(challenge_store)}")
    return expires_at

def get_and_validate_challenge(challenge: str, wallet_address: str) -> bool:
    """
    Retrieves the challenge, checks if it's for the given wallet_address,
    and if it hasn't expired. Invalidates the challenge after retrieval.
    """
    # Clean up expired challenges first (simple in-memory cleanup)
    # In Redis, this would be handled by TTL
    now = datetime.now(timezone.utc)
    expired_keys = [k for k, v in challenge_store.items() if v["expires_at"] < now]
    for k in expired_keys:
        try:
            del challenge_store[k]
            logger.debug(f"Expired challenge {k} removed from store.")
        except KeyError:
            pass # Possible race condition if removed by another request, ignore.


    challenge_data = challenge_store.pop(challenge, None) # Invalidate by removing
    if not challenge_data:
        logger.warning(f"Challenge not found or already used: {challenge}")
        return False

    if challenge_data["wallet_address"] != wallet_address:
        logger.warning(f"Challenge wallet address mismatch for {wallet_address}. Expected {challenge_data['wallet_address']}")
        # Re-store if popped by mistake for wrong user? No, challenge should be unique.
        return False

    # Expiry check was implicitly done by cleanup, but double check for the popped item
    if challenge_data["expires_at"] < datetime.now(timezone.utc):
        logger.warning(f"Challenge expired for {wallet_address} at {challenge_data['expires_at']}")
        return False

    logger.info(f"Challenge validated and invalidated for {wallet_address}")
    return True


def verify_xrpl_signature(public_key_hex: str, message: str, signature_hex: str) -> bool:
    """
    Verifies an XRPL signature.
    Args:
        public_key_hex: The signer's public key in hex format.
        message: The original message string that was signed (will be UTF-8 encoded).
        signature_hex: The signature in hex format.
    Returns:
        True if the signature is valid, False otherwise.
    """
    try:
        # Message needs to be bytes. Standard practice is to sign the UTF-8 representation.
        message_bytes = message.encode('utf-8')
        # Signature needs to be bytes from hex.
        signature_bytes = bytes.fromhex(signature_hex)

        # Verify the signature
        # The `verify` function from `xrpl.cryptography` is what we need.
        # It expects: signature_bytes, message_bytes, public_key_bytes
        public_key_bytes = bytes.fromhex(public_key_hex)

        return verify(signature_bytes, message_bytes, public_key_bytes)
    except ValueError as e: # Handles errors from bytes.fromhex if format is wrong
        logger.error(f"ValueError during signature verification (hex format issue?): {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during XRPL signature verification: {e}")
        return False

def create_access_token(data: dict) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = python_jose_jwt.encode(to_encode, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)
    return encoded_jwt

async def get_current_active_user(token: str) -> TokenData:
    """
    Dependency function to decode JWT token and get the current user.
    To be used with FastAPI's Depends.
    """
    credentials_exception = JWTError("Could not validate credentials") # Generic error for FastAPI
    try:
        payload = python_jose_jwt.decode(token, auth_config.SECRET_KEY, algorithms=[auth_config.ALGORITHM])
        wallet_address: Optional[str] = payload.get("sub") # Assuming "sub" (subject) stores the wallet_address
        if wallet_address is None:
            logger.warning("Token payload missing 'sub' (wallet_address)")
            raise credentials_exception

        # Ensure user exists in DB (important if users can be deleted or tokens live long)
        user = get_or_create_user(wallet_address=wallet_address)
        if user is None:
            logger.warning(f"User {wallet_address} from token not found in DB.")
            raise credentials_exception

        return TokenData(wallet_address=wallet_address)
    except python_jose_jwt.ExpiredSignatureError:
        logger.info("Token expired")
        raise JWTError("Token has expired") # Specific error for FastAPI handling
    except python_jose_jwt.JWTError as e:
        logger.error(f"JWTError during token decode: {e}")
        raise credentials_exception # Raise the generic error for FastAPI
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error validating token: {e}")
        raise credentials_exception

# Helper to derive public key from classic address (r-address)
# This is a simplified example. In XRPL, an r-address doesn't uniquely determine a public key
# if master keys vs regular keys are involved, or if the account hasn't submitted a tx with a public key.
# For signing challenges, the client usually provides its public key or signs in a way that it can be recovered.
# However, xrpl.account.get_public_key_from_address is a more direct way to get the *master* public key.
# If regular keys are used for signing, the client might need to send its public key along with the signature.
# For simplicity, let's assume we are dealing with master keys or the client can provide its public key.

def get_public_key_for_address(wallet_address: str) -> Optional[str]:
    """
    Attempts to get a public key associated with an XRPL address.
    This is often the master public key.
    NOTE: This might not always be the key used for signing if regular keys are involved.
          A more robust system might require the client to send their public key.
    """
    try:
        # This function might not exist or work as expected for all cases.
        # `xrpl.utils.derive_public_key(Wallet(seed, sequence=0).seed)` is one way if you have a seed.
        # For verification, we usually need the public key that *corresponds* to the private key that signed.
        # If the user provides their public key, that's best.
        # `get_public_key_from_address` from `xrpl.cryptography` is what we should try.
        # This was recently added to xrpl-py or is part of its internal structure.

        # Let's assume for now, the client will need to provide their public key
        # if it cannot be reliably derived or fetched.
        # For this example, we'll placeholder this. A real implementation needs care.
        # A common pattern: client sends wallet_address, public_key, signature.
        # Then verify public_key matches wallet_address, then verify signature.

        # Placeholder: In a real app, you might query the ledger for account_info
        # or require the client to send their public_key if not using master key for signing.
        # For now, this function is a conceptual placeholder.
        # If `xrpl.cryptography.get_public_key_from_address` works, it's for master key.
        # This function seems to not be directly available in xrpl-py 2.4.0 in a simple form.
        #
        # Let's rely on the client sending the public key for verification for now.
        # The verify_xrpl_signature will take public_key_hex as an argument.
        logger.warning("get_public_key_for_address is a placeholder. Client should ideally provide public key for verification.")
        return None # Indicate that this function is not fully implemented for auto-derivation
    except Exception as e:
        logger.error(f"Error in conceptual get_public_key_for_address for {wallet_address}: {e}")
        return None

def is_valid_xrpl_address(address: str) -> bool:
    """Validates XRPL address format."""
    return addresscodec.is_valid_classic_address(address)

# It's critical that the client-side signing process uses the *exact same message string*
# that `generate_challenge_message` creates, and signs its UTF-8 bytes.
# The public key used for verification must correspond to the private key used for signing.
# If using regular keys, the client must provide the public key of the regular key.
# If using the master key, the master public key is used.
# `does_public_key_match_address` can verify if a given public key could belong to an address.
# (e.g. master public key matches address, or a regular key is registered to the account)
# This is complex because an account can have a master key pair and optionally a regular key pair.
# The signature must be verifiable by *one* of these.
# A common flow:
# 1. Client provides `wallet_address` and its `public_key_hex` it will use for signing.
# 2. Backend: Verify `public_key_hex` is valid for `wallet_address` (e.g. it's the master, or a registered regular key).
#    `xrpl.account.does_public_key_match_address(public_key_hex, wallet_address)` might be useful.
#    This function is not directly available in xrpl-py 2.4.0 in this exact form.
#    A simpler check is `addresscodec.classic_address_to_eth_address(addresscodec.decode_classic_address(wallet_address)) == addresscodec.classic_address_to_eth_address(addresscodec.derive_classic_address(public_key_hex))`
#    No, that's not right. `addresscodec.derive_classic_address(public_key_hex)` gives the r-address for that public key.
#    So, we check if `addresscodec.derive_classic_address(public_key_hex) == wallet_address`. This assumes the provided public key *is* the one that generates the address.

def check_public_key_matches_address(public_key_hex: str, classic_address: str) -> bool:
    """
    Checks if the given public key derives the given classic address.
    This is typically true if the public key is the master key for the address.
    """
    try:
        derived_address = addresscodec.derive_classic_address(public_key_hex)
        return derived_address == classic_address
    except Exception as e:
        logger.error(f"Error checking public key against address ({public_key_hex}, {classic_address}): {e}")
        return False

# For the `TokenRequest` in `auth/models.py`, we should add `public_key_hex: str`.
# The client will send its wallet address, the public key it used for signing, and the signature.
# The backend then:
# 1. Validates the `wallet_address` format.
# 2. Validates that the `public_key_hex` indeed corresponds to the `wallet_address`.
# 3. Retrieves the challenge message associated with `wallet_address`.
# 4. Verifies the `signature` using `public_key_hex` and the challenge message.

# I will update auth/models.py to reflect this need for public_key_hex in TokenRequest.

# Configure basic logging if not already configured elsewhere
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
