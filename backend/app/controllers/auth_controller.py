"""Authentication controller for handling auth endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from app.models.user import (
    UserRegister,
    UserLogin,
    AuthResponse,
    UserResponse,
    TokenResponse,
    PasswordChangeRequest
)
from app.services.auth_service import AuthService
from app.utils.auth import TokenManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    return parts[1]


def get_current_user(token: str = Depends(get_token_from_header)) -> UserResponse:
    """Get current user from token."""
    user = AuthService.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="User Registration",
    description="Register a new user account"
)
async def register(user_data: UserRegister):
    """
    Register a new user.
    
    - **username**: Username (must be unique, 3-50 characters)
    - **password**: Password (minimum 8 characters)
    - **confirm_password**: Password confirmation (must match password)
    """
    try:
        # Validate password match
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Passwords do not match"
            )

        # Register user
        success, message, user = AuthService.register_user(
            username=user_data.username,
            password=user_data.password
        )

        if success:
            return AuthResponse(
                success=True,
                message=message,
                data={
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "created_at": user.created_at.isoformat()
                }
            )
        else:
            raise HTTPException(status_code=400, detail=message)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Login with username and password to get access token"
)
async def login(credentials: UserLogin):
    """
    Login with username and password.
    
    - **username**: Username
    - **password**: User password
    
    Returns access token and user information.
    """
    try:
        success, message, token_response = AuthService.login_user(
            username=credentials.username,
            password=credentials.password
        )

        if success:
            return token_response
        else:
            raise HTTPException(status_code=401, detail=message)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during login")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get information about the currently authenticated user"
)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.post(
    "/change-password",
    response_model=AuthResponse,
    summary="Change Password",
    description="Change the password for the currently authenticated user"
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Change password for current user.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    - **confirm_password**: Password confirmation (must match new_password)
    """
    try:
        # Validate password match
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="New passwords do not match"
            )

        # Ensure new password is different from current
        if password_data.current_password == password_data.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password must be different from current password"
            )

        # Change password
        success, message = AuthService.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        if success:
            return AuthResponse(success=True, message=message)
        else:
            raise HTTPException(status_code=400, detail=message)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during password change")


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="User Logout",
    description="Logout the current user (client-side token deletion)"
)
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: This is a stateless API. The client should delete the token locally.
    This endpoint just validates the token and returns success.
    """
    logger.info(f"User logged out: {current_user.email}")
    return AuthResponse(
        success=True,
        message="Logout successful. Please delete your token locally."
    )


@router.post(
    "/verify-token",
    response_model=AuthResponse,
    summary="Verify Token",
    description="Verify if a token is valid"
)
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    """Verify if the provided token is valid."""
    return AuthResponse(
        success=True,
        message="Token is valid",
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "username": current_user.username
        }
    )
