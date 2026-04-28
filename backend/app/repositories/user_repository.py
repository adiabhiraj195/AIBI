"""User repository for database operations."""

import logging
from typing import Optional, List
from app.database.connection import DatabaseConnection
from app.models.database_models import User
from app.models.user import UserResponse
from datetime import datetime

logger = logging.getLogger(__name__)


class UserRepository:
    """Handle user database operations."""

    @staticmethod
    def create_user(email: str, username: str, hashed_password: str) -> Optional[int]:
        """Create a new user in the database."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = User(
                    email=email,
                    username=username,
                    password_hash=hashed_password,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"User created: {email}")
                return user.id
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
        return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[dict]:
        """Get user by email."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = session.query(User).filter(User.email == email).first()
                if user:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at
                    }
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
        return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at
                    }
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
        return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """Get user by username."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at
                    }
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching user by username: {e}")
        return None

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists."""
        return UserRepository.get_user_by_email(email) is not None

    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if username already exists."""
        return UserRepository.get_user_by_username(username) is not None

    @staticmethod
    def update_password(user_id: int, new_hashed_password: str) -> bool:
        """Update user password."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.password_hash = new_hashed_password
                    user.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"Password updated for user ID: {user_id}")
                    return True
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error updating password: {e}")
        return False

    @staticmethod
    def get_all_users() -> List[dict]:
        """Get all users (for admin purposes)."""
        try:
            session = DatabaseConnection.get_session()
            try:
                users = session.query(User).order_by(User.created_at.desc()).all()
                return [
                    {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at
                    }
                    for user in users
                ]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
        return []

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user."""
        try:
            session = DatabaseConnection.get_session()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    session.delete(user)
                    session.commit()
                    logger.info(f"User deleted: {user_id}")
                    return True
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
        return False
