# auth/stack_auth.py
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from functools import lru_cache
from api.core.config import settings

security = HTTPBearer()


@lru_cache(maxsize=1)
def get_stack_public_key() -> str:
    """
    Fetch and cache Stack's public key
    Only called once, then cached
    """
    # Stack usually provides JWKS endpoint
    # Check your Stack dashboard for the exact URL
    response = httpx.get(
        f"https://api.stack-auth.com/api/v1/projects/{settings.NEXT_PUBLIC_STACK_PROJECT_ID}/.well-known/jwks.json"
    )
    response.raise_for_status()
    jwks = response.json()
    # Extract the public key from JWKS
    # This depends on Stack's JWKS format
    return jwks["keys"][0]  # Adjust based on Stack's format


async def verify_stack_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    Verify JWT token locally (fast, no API call)
    """
    token = credentials.credentials

    try:
        # Decode and verify JWT locally
        payload = jwt.decode(
            token,
            get_stack_public_key(),  # Cached public key
            algorithms=["ES256"],
            audience=settings.NEXT_PUBLIC_STACK_PROJECT_ID,
            options={"verify_exp": True},  # Verify expiration
        )

        return {"id": payload.get("sub"), "email": payload.get("email")}

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
