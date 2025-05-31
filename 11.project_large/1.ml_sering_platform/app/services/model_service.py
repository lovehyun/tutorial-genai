# app/services/model_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
import logging
from typing import List, Optional
from ..db.models.model import Model
from ..db.models.user import User
from ..db.crud.model_crud import ModelCRUD
from ..schemas.model import ModelCreate, ModelUpdate
from ..utils.file_handler import validate_model_file, save_model_file, delete_model_file
from ..utils.validators import validate_model_name
import os
from ..core.config import settings

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self.model_crud = ModelCRUD(db)
    
    async def create_model(self, name: str, type: str, framework: str, description: str, file: Optional[UploadFile], file_path: Optional[str], user_id: int) -> Model:
        """Create a new model"""
        logger.debug(f"[DEBUG] Creating model: {name} for user {user_id}")
        
        try:
            if file:
                # 파일 업로드 방식
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in ['.h5', '.pkl', '.pt', '.pth', '.onnx']:
                    raise ValueError(f"Unsupported file format: {file_ext}")
                
                # 파일 저장
                file_path = os.path.join(settings.UPLOAD_DIR, "models", f"user_{user_id}", f"{name}{file_ext}")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(await file.read())
            elif file_path:
                # 로컬 경로 방식
                if not os.path.exists(file_path):
                    raise ValueError(f"File not found at path: {file_path}")
                
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in ['.h5', '.pkl', '.pt', '.pth', '.onnx']:
                    raise ValueError(f"Unsupported file format: {file_ext}")
                
                # 파일 복사
                new_path = os.path.join(settings.UPLOAD_DIR, "models", f"user_{user_id}", f"{name}{file_ext}")
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                with open(file_path, "rb") as src, open(new_path, "wb") as dst:
                    dst.write(src.read())
                file_path = new_path
            else:
                raise ValueError("Either file or file_path must be provided")
            
            # 모델 생성
            model = self.model_crud.create(
                user_id=user_id,
                name=name,
                description=description,
                type=type,
                framework=framework,
                path=file_path,
                is_active=True
            )
            
            return model
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_models(self, user_id: int) -> List[Model]:
        """Get all models for a user"""
        try:
            logger.info(f"ModelService: Getting models for user_id {user_id}")
            models = self.model_crud.get_by_user_id(user_id)
            logger.info(f"ModelService: Retrieved {len(models)} models for user {user_id}")
            if not models:
                logger.info(f"ModelService: No models found for user {user_id}")
            return models
        except Exception as e:
            logger.error(f"ModelService: Error getting models: {str(e)}", exc_info=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_model(self, model_id: int, user_id: int) -> Model:
        """Get a specific model"""
        try:
            model = self.model_crud.get(model_id)
            if not model or model.user_id != user_id:
                raise HTTPException(status_code=404, detail="Model not found")
            return model
        except Exception as e:
            logger.error(f"Error getting model: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def update_model(self, model_id: int, user_id: int, name: Optional[str] = None,
                    description: Optional[str] = None, type: Optional[str] = None,
                    file: Optional[UploadFile] = None) -> Model:
        """Update a model"""
        try:
            model = self.get_model(model_id, user_id)
            
            # Update basic info
            if name is not None:
                if not validate_model_name(name):
                    raise HTTPException(status_code=400, detail="Invalid model name")
                model.name = name
            if description is not None:
                model.description = description
            if type is not None:
                model.type = type
            
            # Update file if provided
            if file is not None:
                if not validate_model_file(file):
                    raise HTTPException(status_code=400, detail="Invalid model file")
                
                # Delete old file
                if model.path:
                    delete_model_file(model.path)
                
                # Save new file
                file_path, file_size = save_model_file(file, user_id, model.id)
                model.path = file_path
            
            self.db.commit()
            logger.info(f"Model updated: {model_id}")
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating model: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def delete_model(self, model_id: int, user_id: int) -> bool:
        """Delete a model"""
        try:
            model = self.get_model(model_id, user_id)
            
            # Delete file
            if model.path:
                delete_model_file(model.path)
            
            # Delete record
            self.model_crud.delete(model_id)
            self.db.commit()
            
            logger.info(f"Model deleted: {model_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting model: {e}")
            raise HTTPException(status_code=500, detail=str(e))
