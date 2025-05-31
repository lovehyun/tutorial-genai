# app/services/endpoint_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..db.crud.endpoint_crud import EndpointCRUD
from ..schemas.endpoint import EndpointCreate, EndpointUpdate, EndpointResponse
from ..db.models.endpoint import Endpoint
from ..db.models.model import Model
from ..db.models.api_key import APIKey
from ..core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class EndpointService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = EndpointCRUD(db)

    def _get_model_name(self, model_id: int) -> str:
        """Get model name by ID"""
        model = self.db.query(Model).filter(Model.id == model_id).first()
        return model.name if model else "Unknown Model"

    def _get_api_key(self, api_key_id: Optional[int]) -> Optional[str]:
        """Get API key by ID"""
        if not api_key_id:
            return None
        api_key = self.db.query(APIKey).filter(APIKey.id == api_key_id).first()
        return api_key.key if api_key else None

    def get_endpoints(self, user_id: int) -> List[EndpointResponse]:
        """Get all endpoints for a user"""
        logger.info(f"EndpointService: Getting endpoints for user_id {user_id}")
        endpoints = self.crud.get_endpoints(user_id)
        logger.info(f"EndpointService: Retrieved {len(endpoints)} endpoints for user {user_id}")
        
        # Convert to response model with URLs and related info
        return [
            EndpointResponse(
                **endpoint.__dict__,
                url=f"/api/v1/inference/{endpoint.path}",
                ml_model_title=self._get_model_name(endpoint.ml_model_id),
                api_key=self._get_api_key(endpoint.api_key_id)
            )
            for endpoint in endpoints
        ]

    def get_endpoint(self, endpoint_id: int) -> Optional[EndpointResponse]:
        """Get a specific endpoint"""
        logger.info(f"EndpointService: Getting endpoint {endpoint_id}")
        endpoint = self.crud.get_endpoint(endpoint_id)
        if not endpoint:
            logger.info(f"EndpointService: Endpoint {endpoint_id} not found")
            return None
        
        return EndpointResponse(
            **endpoint.__dict__,
            url=f"/api/v1/inference/{endpoint.path}",
            ml_model_title=self._get_model_name(endpoint.ml_model_id),
            api_key=self._get_api_key(endpoint.api_key_id)
        )

    def create_endpoint(self, endpoint: EndpointCreate, user_id: int) -> EndpointResponse:
        """Create a new endpoint"""
        logger.info(f"EndpointService: Creating endpoint for user {user_id}")
        # Check if model exists and belongs to user
        model = self.db.query(Model).filter(Model.id == endpoint.ml_model_id).first()
        if not model or model.user_id != user_id:
            raise HTTPException(status_code=404, detail="Model not found")

        # Check if API key exists and belongs to user if provided
        if endpoint.api_key_id:
            api_key = self.db.query(APIKey).filter(APIKey.id == endpoint.api_key_id).first()
            if not api_key or api_key.user_id != user_id:
                raise HTTPException(status_code=404, detail="API key not found")

        # Create endpoint
        db_endpoint = self.crud.create_endpoint(endpoint, user_id)

        # Get model and API key for response
        model = self.db.query(Model).filter(Model.id == db_endpoint.ml_model_id).first()
        api_key = self.db.query(APIKey).filter(APIKey.id == db_endpoint.api_key_id).first() if db_endpoint.api_key_id else None

        # Construct response
        return EndpointResponse(
            **db_endpoint.__dict__,
            url=f"/api/v1/inference/{db_endpoint.path}",
            ml_model_title=model.name if model else "Unknown",
            api_key=api_key.key if api_key else None
        )

    def update_endpoint(self, endpoint_id: int, endpoint_update: EndpointUpdate) -> Optional[EndpointResponse]:
        """Update an endpoint"""
        logger.info(f"EndpointService: Updating endpoint {endpoint_id}")
        db_endpoint = self.crud.update_endpoint(endpoint_id, endpoint_update)
        if not db_endpoint:
            return None
        
        return EndpointResponse(
            **db_endpoint.__dict__,
            url=f"/api/v1/inference/{db_endpoint.path}",
            ml_model_title=self._get_model_name(db_endpoint.ml_model_id),
            api_key=self._get_api_key(db_endpoint.api_key_id)
        )

    def delete_endpoint(self, endpoint_id: int) -> bool:
        """Delete an endpoint"""
        logger.info(f"EndpointService: Deleting endpoint {endpoint_id}")
        return self.crud.delete_endpoint(endpoint_id) 