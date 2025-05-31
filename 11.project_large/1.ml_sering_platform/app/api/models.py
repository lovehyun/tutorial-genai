# app/api/models.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import logging
import traceback
from ..core.dependencies import get_current_user
from ..db.session import get_db
from ..db.crud.model_crud import ModelCRUD
from ..schemas.model import ModelCreate, ModelUpdate, ModelResponse
from ..services.model_service import ModelService
from ..schemas.user import User
import os
from io import BytesIO
from fastapi import status

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/models", tags=["models"])

@router.get("", response_model=List[ModelResponse])
async def get_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all models for the current user"""
    logger.debug(f"[DEBUG] Getting models for user {current_user.id}")
    model_service = ModelService(db)
    models = model_service.get_models(current_user.id)
    logger.debug(f"[DEBUG] Retrieved models from database: {models}")
    
    if not models:
        logger.debug("[DEBUG] No models found, returning empty list")
        return []
    
    return models

@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    name: str = Form(...),
    type: str = Form(...),
    framework: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(None),
    file_path: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new model"""
    logger.debug(f"[DEBUG] Creating model for user {current_user.id}")
    logger.debug(f"[DEBUG] Received parameters: name={name}, type={type}, framework={framework}, description={description}")
    logger.debug(f"[DEBUG] File: {file}, File path: {file_path}")
    
    if not file and not file_path:
        logger.error("[ERROR] Neither file nor file_path provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file or file_path must be provided"
        )
    
    model_service = ModelService(db)
    return await model_service.create_model(
        name=name,
        type=type,
        framework=framework,
        description=description,
        file=file,
        file_path=file_path,
        user_id=current_user.id
    )

@router.get("/{model_id}", response_model=List[ModelResponse])
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific model"""
    logger.debug(f"[DEBUG] Getting model {model_id} for user {current_user.id}")
    model_service = ModelService(db)
    model = model_service.get_model(model_id, current_user.id)
    
    if not model:
        logger.debug(f"[DEBUG] Model {model_id} not found")
        return []
    
    return [model]

@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a model"""
    logger.debug(f"[DEBUG] Deleting model {model_id} for user {current_user.id}")
    model_service = ModelService(db)
    return model_service.delete_model(model_id, current_user.id)
