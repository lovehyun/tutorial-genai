# app/api/api_keys.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from ..core.dependencies import get_current_user
from ..db.session import get_db
from ..db.crud.api_key_crud import APIKeyCRUD
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from ..services.api_key_service import APIKeyService
from ..schemas.user import User
from fastapi import status

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.get("", response_model=List[APIKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all API keys for the current user"""
    logger.debug(f"[DEBUG] Getting API keys for user {current_user.id}")
    api_key_service = APIKeyService(db)
    api_keys = api_key_service.get_api_keys(current_user.id)
    logger.debug(f"[DEBUG] Retrieved API keys from database: {api_keys}")
    
    if not api_keys:
        logger.debug("[DEBUG] No API keys found, returning empty list")
        return []
    
    return api_keys

@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    logger.debug(f"[DEBUG] Creating API key for user {current_user.id}")
    api_key_service = APIKeyService(db)
    return api_key_service.create_api_key(api_key, current_user.id)

@router.get("/{api_key_id}", response_model=List[APIKeyResponse])
async def get_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific API key"""
    logger.debug(f"[DEBUG] Getting API key {api_key_id} for user {current_user.id}")
    api_key_service = APIKeyService(db)
    api_key = api_key_service.get_api_key(api_key_id)
    
    if not api_key:
        logger.debug(f"[DEBUG] API key {api_key_id} not found")
        return []
    
    return [api_key]

@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    logger.debug(f"[DEBUG] Deleting API key {api_key_id} for user {current_user.id}")
    api_key_service = APIKeyService(db)
    return api_key_service.delete_api_key(api_key_id)
