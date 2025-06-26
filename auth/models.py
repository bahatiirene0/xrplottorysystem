from pydantic import BaseModel, Field

class ChallengeRequest(BaseModel):
    wallet_address: str = Field(..., description="User's wallet address initiating the login process")

class ChallengeResponse(BaseModel):
    message_to_sign: str = Field(..., description="The unique message the user needs to sign with their private key")
    expires_at: str = Field(..., description="ISO timestamp indicating when the challenge expires")

class TokenRequest(BaseModel):
    wallet_address: str = Field(..., description="User's wallet address")
    public_key_hex: str = Field(..., description="The hex-encoded public key used for signing the challenge")
    # The signature is typically a hex-encoded string
    signature: str = Field(..., description="Hex-encoded signature of the challenge message")
    challenge_message: str = Field(..., description="The original challenge message that was signed") # Client needs to send this back

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data a JWT token will carry."""
    wallet_address: str | None = None

class AuthConfig(BaseModel):
    """Configuration for JWT settings."""
    SECRET_KEY: str = "a_very_secret_key_please_change_in_production" # TODO: Load from env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CHALLENGE_EXPIRE_MINUTES: int = 5

# Instantiate config - in a real app, load from environment variables
auth_config = AuthConfig()
