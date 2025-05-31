from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.model import Model
from ...schemas.model import ModelCreate, ModelUpdate
import logging
from ..models.user import User
from datetime import datetime

class ModelCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get(self, model_id: int) -> Optional[Model]:
        """Get a model by ID"""
        return self.db.query(Model).filter(Model.id == model_id).first()

    def get_by_user_id(self, user_id: int) -> List[Model]:
        """Get all models for a user"""
        logger = logging.getLogger(__name__)
        logger.info(f"ModelCRUD: Querying models for user_id {user_id}")
        models = self.db.query(Model).filter(Model.user_id == user_id).all()
        logger.info(f"ModelCRUD: Found {len(models)} models for user_id {user_id}")
        return models

    def create(self, user_id: int, name: str, description: Optional[str], 
               type: str, framework: str, path: str, is_active: bool = True) -> Model:
        """Create a new model"""
        model = Model(
            user_id=user_id,
            name=name,
            description=description,
            type=type,
            framework=framework,
            path=path,
            is_active=is_active
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update(self, model_id: int, **kwargs) -> Optional[Model]:
        """Update a model"""
        model = self.get(model_id)
        if model:
            for key, value in kwargs.items():
                setattr(model, key, value)
            self.db.commit()
            self.db.refresh(model)
        return model

    def delete(self, model_id: int) -> bool:
        """Delete a model"""
        model = self.get(model_id)
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False

def get_model(db: Session, model_id: int) -> Optional[Model]:
    """Get a model by its ID"""
    return db.query(Model).filter(Model.id == model_id).first()

def get_models(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Model]:
    """Get all models for a user"""
    return db.query(Model).filter(
        Model.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_model(
    db: Session,
    name: str,
    model_type: str,
    user_id: int,
    description: Optional[str] = None,
    file_path: Optional[str] = None
) -> Model:
    """Create a new model"""
    db_model = Model(
        name=name,
        model_type=model_type,
        user_id=user_id,
        description=description,
        file_path=file_path
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def update_model(
    db: Session,
    model_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    file_path: Optional[str] = None
) -> Optional[Model]:
    """Update a model"""
    db_model = get_model(db, model_id)
    if db_model:
        if name is not None:
            db_model.name = name
        if description is not None:
            db_model.description = description
        if file_path is not None:
            db_model.file_path = file_path
        db_model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_model)
    return db_model

def delete_model(db: Session, model_id: int) -> bool:
    """Delete a model"""
    db_model = get_model(db, model_id)
    if db_model:
        db.delete(db_model)
        db.commit()
        return True
    return False 