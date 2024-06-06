"""Auth router"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.security.oauth2 import OAuth2PasswordRequestForm as LoginSchema
from starlette.requests import Request

from src.config import SCHEDULER_API_KEY
from src.service import login, oauth2_scheme, get_refresh_token, logout, token_is_valid

router = APIRouter(prefix="/auth", tags=["Auth"])
api_key_header = APIKeyHeader(name="X-API-Key")


@router.post("/login/")
async def login_route(
    request: Request,
    login_schema: LoginSchema = Depends(),
):
    """Login a user"""
    response_data = await login(
        login_schema.username, login_schema.password, request.state.clinic
    )
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/refresh-token/")
async def refresh_token(
    request: Request, token: Annotated[str, Depends(oauth2_scheme)]
):
    """Refresh a token"""
    response_data = await get_refresh_token(token, request.state.clinic)
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("/check-token/")
async def check_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    key_header=Security(api_key_header),
):
    """Check a token"""
    if key_header == SCHEDULER_API_KEY and token_is_valid(token):
        return JSONResponse({"message": "Valid token"})
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
    )


@router.post("/logout/")
async def logout_route(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    """Logout a user"""
    await logout(token, request.state.clinic)
    return JSONResponse(content={}, status_code=status.HTTP_200_OK)
