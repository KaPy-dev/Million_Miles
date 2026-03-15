from fastapi import APIRouter, HTTPException, status

from auth import create_access_token, verify_credentials
from schemas import TokenRequest, TokenResponse
import logging as logger 
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def login(body: TokenRequest) -> TokenResponse:
    logger.warning("Login attempt")
    logger.debug("Received request: %s", body)
    if not verify_credentials(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": body.username})
    return TokenResponse(access_token=token)
