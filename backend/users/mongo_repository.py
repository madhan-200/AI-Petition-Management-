"""
MongoDB Repository for Users

Handles User data storage and retrieval in MongoDB.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_collection
from django.contrib.auth.hashers import make_password, check_password
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for User operations in MongoDB."""
    
    COLLECTION_NAME = 'users'
    
    @staticmethod
    def _get_collection():
        """Get users collection."""
        return get_collection(UserRepository.COLLECTION_NAME)
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'CITIZEN') -> Optional[Dict]:
        """
        Create a new user in MongoDB.
        
        Args:
            username: User's username
            email: User's email
            password: Plain text password (will be hashed)
            role: User role (CITIZEN, OFFICER, ADMIN)
        
        Returns:
            Created user document or None
        """
        collection = UserRepository._get_collection()
        if collection is None:
            logger.error("MongoDB collection not available")
            return None
        
        try:
            # Check if user exists
            if collection.find_one({'username': username}):
                logger.warning(f"User {username} already exists")
                return None
            
            user_doc = {
                'username': username,
                'email': email,
                'password': make_password(password),
                'role': role,
                'is_active': True,
                'is_staff': role == 'ADMIN',
                'is_superuser': role == 'ADMIN',
                'date_joined': datetime.utcnow(),
                'last_login': None
            }
            
            result = collection.insert_one(user_doc)
            user_doc['_id'] = result.inserted_id
            
            logger.info(f"✅ User created in MongoDB: {username}")
            return user_doc
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Get user by username."""
        collection = UserRepository._get_collection()
        if collection is None:
            return None
        
        return collection.find_one({'username': username})
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Get user by MongoDB ObjectId."""
        collection = UserRepository._get_collection()
        if collection is None:
            return None
        
        try:
            return collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with username and password.
        
        Returns:
            User document if authenticated, None otherwise
        """
        user = UserRepository.get_user_by_username(username)
        if user and check_password(password, user['password']):
            # Update last login
            collection = UserRepository._get_collection()
            if collection is not None:
                collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
            return user
        return None
    
    @staticmethod
    def get_all_users(role: Optional[str] = None) -> List[Dict]:
        """Get all users, optionally filtered by role."""
        collection = UserRepository._get_collection()
        if collection is None:
            return []
        
        query = {'role': role} if role else {}
        return list(collection.find(query))
    
    @staticmethod
    def update_user(user_id: str, updates: Dict) -> bool:
        """Update user document."""
        collection = UserRepository._get_collection()
        if collection is None:
            return False
        
        try:
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user from MongoDB."""
        collection = UserRepository._get_collection()
        if collection is None:
            return False
        
        try:
            result = collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False
