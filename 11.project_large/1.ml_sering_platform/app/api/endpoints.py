# app/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.session import get_db
from ..schemas.endpoint import EndpointCreate, EndpointResponse, EndpointUpdate
from ..services.endpoint_service import EndpointService
from ..core.dependencies import get_current_user
from ..db.models.user import User
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/endpoints", tags=["endpoints"])

@router.get("", response_model=List[EndpointResponse])
async def get_endpoints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all endpoints for the current user"""
    logger.debug(f"[DEBUG] Getting endpoints for user {current_user.id}")
    endpoint_service = EndpointService(db)
    endpoints = endpoint_service.get_endpoints(current_user.id)
    logger.debug(f"[DEBUG] Retrieved endpoints from database: {endpoints}")
    
    if not endpoints:
        logger.debug("[DEBUG] No endpoints found, returning empty list")
        return []
    
    return endpoints

@router.get("/{endpoint_id}", response_model=List[EndpointResponse])
async def get_endpoint(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific endpoint"""
    logger.debug(f"[DEBUG] Getting endpoint {endpoint_id} for user {current_user.id}")
    endpoint_service = EndpointService(db)
    endpoint = endpoint_service.get_endpoint(endpoint_id)
    
    if not endpoint:
        logger.debug(f"[DEBUG] Endpoint {endpoint_id} not found")
        return []
    
    return [endpoint]

@router.post("", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    endpoint: EndpointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new endpoint"""
    logger.debug(f"[DEBUG] Creating endpoint for user {current_user.id}")
    endpoint_service = EndpointService(db)
    try:
        return endpoint_service.create_endpoint(endpoint, current_user.id)
    except IntegrityError as e:
        if "UNIQUE constraint failed: endpoints.path" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An endpoint with this path already exists. Please choose a different path."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the endpoint"
        )

@router.put("/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(
    endpoint_id: int,
    endpoint_update: EndpointUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an endpoint"""
    logger.debug(f"[DEBUG] Updating endpoint {endpoint_id} for user {current_user.id}")
    endpoint_service = EndpointService(db)
    return endpoint_service.update_endpoint(endpoint_id, endpoint_update)

@router.delete("/{endpoint_id}")
async def delete_endpoint(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an endpoint"""
    logger.debug(f"[DEBUG] Deleting endpoint {endpoint_id} for user {current_user.id}")
    endpoint_service = EndpointService(db)
    return endpoint_service.delete_endpoint(endpoint_id) 