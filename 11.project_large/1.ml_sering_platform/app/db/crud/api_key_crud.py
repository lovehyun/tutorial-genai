from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.api_key import APIKey
from ...schemas.api_key import APIKeyCreate, APIKeyUpdate
from ...core.security import generate_api_key
import secrets
from datetime import datetime

class APIKeyCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get(self, api_key_id: int) -> Optional[APIKey]:
        """Get an API key by ID"""
        return self.db.query(APIKey).filter(APIKey.id == api_key_id).first()

    def get_by_user_id(self, user_id: int) -> List[APIKey]:
        """Get all API keys for a user"""
        return self.db.query(APIKey).filter(APIKey.user_id == user_id).all()

    def create(self, user_id: int, name: str, description: Optional[str], key: str) -> APIKey:
        """Create a new API key"""
        api_key = APIKey(
            user_id=user_id,
            name=name,
            description=description,
            key=key,
            is_active=True
        )
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key

    def update(self, api_key_id: int, **kwargs) -> Optional[APIKey]:
        """Update an API key"""
        api_key = self.get(api_key_id)
        if api_key:
            for key, value in kwargs.items():
                setattr(api_key, key, value)
            self.db.commit()
            self.db.refresh(api_key)
        return api_key

    def delete(self, api_key_id: int) -> bool:
        """Delete an API key"""
        api_key = self.get(api_key_id)
        if api_key:
            self.db.delete(api_key)
            self.db.commit()
            return True
        return False

    def update_last_used(self, api_key_id: int):
        db_api_key = self.get(api_key_id)
        if db_api_key:
            db_api_key.last_used_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_api_key)
        return db_api_key 