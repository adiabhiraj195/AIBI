"""Authentication service for handling auth business logic."""

import logging
from typing import Optional, Tuple
from app.repositories.user_repository import UserRepository
from app.models.user import UserResponse, TokenResponse
from app.utils.auth import PasswordManager, TokenManager

logger = logging.getLogger(__name__)


class AuthService:
    """Handle authentication business logic."""

    @staticmethod
    def register_user(username: str, password: str) -> Tuple[bool, str, Optional[UserResponse]]:
        """
        Register a new user.
        
        Returns: (success, message, user)
        """
        # Validate input
        if not username or not password:
            return False, "Username and password are required", None

        # Check if username already exists
        if UserRepository.username_exists(username):
            return False, "Username already taken", None

        # Generate email from username (optional, for internal use)
        if '@' in username:
            email = username
        else:
            email = f"{username}@local.app"

        # Hash password
        hashed_password = PasswordManager.hash_password(password)

        # Create user
        user_id = UserRepository.create_user(email, username, hashed_password)
        if user_id:
            user_data = UserRepository.get_user_by_id(user_id)
            if user_data:
                user = UserResponse(**user_data)
                return True, "User registered successfully", user
        
        return False, "Failed to create user", None

    @staticmethod
    def login_user(username: str, password: str) -> Tuple[bool, str, Optional[TokenResponse]]:
        """
        Login a user and return access token.
        
        Returns: (success, message, token_response)
        """
        # Validate input
        if not username or not password:
            return False, "Username and password are required", None

        # Get user by username
        user_data = UserRepository.get_user_by_username(username)
        if not user_data:
            return False, "Invalid username or password", None

        # Verify password
        if not PasswordManager.verify_password(password, user_data['password_hash']):
            return False, "Invalid username or password", None

        # Create access token
        token = TokenManager.create_access_token(
            data={"user_id": str(user_data['id']), "username": user_data['username']}
        )

        # Create response
        user = UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            username=user_data['username'],
            created_at=user_data['created_at'],
            updated_at=user_data['updated_at']
        )

        token_response = TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )

        logger.info(f"User logged in: {username}")
        return True, "Login successful", token_response

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password.
        
        Returns: (success, message)
        """
        # Get user
        user_data = UserRepository.get_user_by_id(user_id)
        if not user_data:
            return False, "User not found"

        # Get full user data with password hash
        user_with_pwd = UserRepository.get_user_by_email(user_data['email'])
        if not user_with_pwd:
            return False, "User not found"

        # Verify current password
        if not PasswordManager.verify_password(current_password, user_with_pwd['password_hash']):
            return False, "Current password is incorrect"

        # Hash new password
        new_hashed_password = PasswordManager.hash_password(new_password)

        # Update password
        if UserRepository.update_password(user_id, new_hashed_password):
            logger.info(f"Password changed for user ID: {user_id}")
            return True, "Password changed successfully"
        
        return False, "Failed to change password"

    @staticmethod
    def get_current_user(token: str) -> Optional[UserResponse]:
        """Get current user from token."""
        user_id = TokenManager.get_user_id_from_token(token)
        if not user_id:
            return None

        user_data = UserRepository.get_user_by_id(user_id)
        if user_data:
            return UserResponse(**user_data)
        return None
