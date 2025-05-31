# app/db/crud/endpoint_crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..models.endpoint import Endpoint
from ...schemas.endpoint import EndpointCreate, EndpointUpdate
from ..models.model import Model
from ..models.api_key import APIKey
from ..models.user import User
from ..base import Base
from datetime import datetime

logger = logging.getLogger(__name__)

class EndpointCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_endpoints(self, user_id: int) -> List[Endpoint]:
        """Get all endpoints for a user"""
        logger.info(f"EndpointCRUD: Querying endpoints for user_id {user_id}")
        endpoints = self.db.query(Endpoint).filter(Endpoint.user_id == user_id).all()
        logger.info(f"EndpointCRUD: Found {len(endpoints)} endpoints for user_id {user_id}")
        return endpoints

    def get_endpoint(self, endpoint_id: int) -> Optional[Endpoint]:
        """Get a specific endpoint"""
        return self.db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()

    def create_endpoint(self, endpoint: EndpointCreate, user_id: int) -> Endpoint:
        """Create a new endpoint"""
        db_endpoint = Endpoint(
            name=endpoint.name,
            description=endpoint.description,
            ml_model_id=endpoint.ml_model_id,
            api_key_id=endpoint.api_key_id,
            require_auth=endpoint.require_auth,
            path=endpoint.path,
            is_active=endpoint.is_active,
            user_id=user_id
        )
        self.db.add(db_endpoint)
        self.db.commit()
        self.db.refresh(db_endpoint)
        return db_endpoint

    def update_endpoint(self, endpoint_id: int, endpoint_update: EndpointUpdate) -> Optional[Endpoint]:
        """Update an endpoint"""
        db_endpoint = self.get_endpoint(endpoint_id)
        if not db_endpoint:
            return None

        update_data = endpoint_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_endpoint, field, value)

        self.db.commit()
        self.db.refresh(db_endpoint)
        return db_endpoint

    def delete_endpoint(self, endpoint_id: int) -> bool:
        """Delete an endpoint"""
        db_endpoint = self.get_endpoint(endpoint_id)
        if not db_endpoint:
            return False

        self.db.delete(db_endpoint)
        self.db.commit()
        return True

    def get_endpoint_by_path(self, path: str) -> Optional[Endpoint]:
        """Get an endpoint by its path"""
        return self.db.query(Endpoint).filter(Endpoint.path == path).first()

def create_endpoint(
    db: Session,
    name: str,
    ml_model_id: int,
    user_id: int,
    description: Optional[str] = None,
    api_key_id: Optional[int] = None,
    require_auth: bool = False,
    path: str = None
) -> Endpoint:
    db_endpoint = Endpoint(
        name=name,
        ml_model_id=ml_model_id,
        user_id=user_id,
        description=description,
        api_key_id=api_key_id,
        require_auth=require_auth,
        path=path
    )
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

def get_endpoint(db: Session, endpoint_id: int) -> Optional[Endpoint]:
    return db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()

def get_endpoint_by_path(db: Session, path: str) -> Optional[Endpoint]:
    return db.query(Endpoint).filter(Endpoint.path == path).first()

def get_endpoints(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Endpoint]:
    return db.query(Endpoint).filter(
        Endpoint.user_id == user_id
    ).offset(skip).limit(limit).all()

def update_endpoint(
    db: Session,
    endpoint_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    api_key_id: Optional[int] = None,
    require_auth: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> Optional[Endpoint]:
    db_endpoint = get_endpoint(db, endpoint_id)
    if db_endpoint:
        if name is not None:
            db_endpoint.name = name
        if description is not None:
            db_endpoint.description = description
        if api_key_id is not None:
            db_endpoint.api_key_id = api_key_id
        if require_auth is not None:
            db_endpoint.require_auth = require_auth
        if is_active is not None:
            db_endpoint.is_active = is_active
        db_endpoint.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_endpoint)
    return db_endpoint

def delete_endpoint(db: Session, endpoint_id: int) -> bool:
    db_endpoint = get_endpoint(db, endpoint_id)
    if db_endpoint:
        db.delete(db_endpoint)
        db.commit()
        return True
    return False

def get_api_key(db: Session, api_key_id: int) -> Optional[APIKey]:
    return db.query(APIKey).filter(APIKey.id == api_key_id).first() 