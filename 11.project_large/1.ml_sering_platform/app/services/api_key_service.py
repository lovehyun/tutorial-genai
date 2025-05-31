# app/services/api_key_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
from typing import List
from datetime import datetime
from ..db.models.api_key import APIKey
from ..db.models.user import User
from ..db.crud.api_key_crud import APIKeyCRUD
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate
from ..core.security import generate_api_key, verify_api_key

logger = logging.getLogger(__name__)

class APIKeyService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = APIKeyCRUD(db)
    
    def create_api_key(self, api_key: APIKeyCreate, user_id: int) -> APIKey:
        """Create a new API key"""
        logger.info(f"Creating API key for user {user_id}")
        key = generate_api_key()
        return self.crud.create(user_id, api_key.name, api_key.description, key)
    
    def get_api_keys(self, user_id: int) -> list[APIKey]:
        return self.crud.get_by_user_id(user_id)
    
    def get_api_key(self, key_id: int) -> APIKey:
        return self.crud.get_by_id(key_id)
    
    def update_api_key(self, key_id: int, api_key: APIKeyUpdate) -> APIKey:
        return self.crud.update(key_id, api_key)
    
    def delete_api_key(self, key_id: int) -> bool:
        return self.crud.delete(key_id)
    
    def verify_api_key(self, api_key: str) -> bool:
        return verify_api_key(api_key)
    
    def update_last_used(self, key_id: int) -> APIKey:
        return self.crud.update_last_used(key_id)

    def get_user_api_keys(self, user: User) -> List[APIKey]:
        """Get all API keys for a user"""
        logger.debug(f"Getting API keys for user: {user.username}")
        
        api_keys = self.crud.get_by_owner_id(user.id)
        
        logger.debug(f"Found {len(api_keys)} API keys for user: {user.username}")
        return api_keys
    
    def toggle_api_key(self, api_key_id: int, user: User) -> APIKey:
        """Toggle API key active status"""
        logger.info(f"Toggling API key {api_key_id} for user: {user.username}")
        
        api_key = self.get_api_key(api_key_id)
        api_key.is_active = not api_key.is_active
        
        self.db.commit()
        self.db.refresh(api_key)
        
        logger.info(f"API key toggled: {api_key.name} -> {'active' if api_key.is_active else 'inactive'}")
        return api_key
