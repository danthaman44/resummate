"""
User router for handling user registration and management.
"""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from api.auth.stack_auth import verify_stack_token
from api.core.schemas import User
from api.db.service import create_or_update_user
from api.core.dependencies import SupabaseClient


router = APIRouter(prefix="/api/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""

    id: str
    displayName: str | None = None
    primaryEmail: str | None = None
    primaryEmailVerified: bool = False
    profileImageUrl: str | None = None


class UserRegisterResponse(BaseModel):
    """Response model for user registration."""

    status: str
    message: str
    user_id: str


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_200_OK,
)
async def register_user(
    supabase: SupabaseClient,
    http_request: Request,
    request: UserRegisterRequest,
    auth_user: dict = Depends(verify_stack_token),
) -> UserRegisterResponse:
    """
    Register a new user.

    Args:
        supabase: Supabase client dependency
        http_request: FastAPI request object
        request: User registration request with user details
        auth_user: Authenticated user data from JWT token

    Returns:
        UserRegisterResponse: Registration success response
    """
    # Verify that the authenticated user matches the request user
    if auth_user.get("id") != request.id:
        return UserRegisterResponse(
            status="error",
            message="User ID mismatch with authentication token",
            user_id=request.id,
        )

    user = User(
        id=request.id,
        displayName=request.displayName,
        primaryEmail=request.primaryEmail,
        primaryEmailVerified=request.primaryEmailVerified,
        profileImageUrl=request.profileImageUrl,
    )
    try:
        data = create_or_update_user(supabase, user)
        if data:
            return UserRegisterResponse(
                status="success",
                message="User registered successfully",
                user_id=request.id,
            )
        else:
            return UserRegisterResponse(
                status="error",
                message="Failed to create or update user",
                user_id=request.id,
            )
    except Exception as e:
        return UserRegisterResponse(
            status="error",
            message=f"Error creating or updating user: {e}",
            user_id=request.id,
        )
