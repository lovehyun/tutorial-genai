# app/api/inference.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Header
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional
from ..db.database import get_db
from ..core.dependencies import get_current_user
from ..schemas.inference import InferenceRequest, InferenceResponse, InferenceResult
from ..schemas.user import User
from ..services.inference_service import InferenceService
from ..db.models.endpoint import Endpoint
from ..db.models.api_key import APIKey
from ..core.security import verify_api_key
from ..db.crud import endpoint_crud, model_crud, api_key_crud
from ..core.config import settings
import joblib
import numpy as np
from ..core.redis_client import get_redis
import json
import uuid
from worker.tasks import process_inference

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inference",
    tags=["inference"]
)

@router.post("/predict", response_model=InferenceResponse)
async def predict(
    request: InferenceRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """추론 요청 제출"""
    inference_service = InferenceService(db)
    return await inference_service.submit_inference(request, background_tasks)

@router.post("/{endpoint_path}")
async def submit_inference(
    endpoint_path: str,
    request_data: Dict[str, Any],
    x_api_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """Submit inference request to queue."""
    try:
        endpoint = endpoint_crud.get_endpoint_by_path(db, endpoint_path)
        if not endpoint:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        # Verify API key if required
        if endpoint.require_auth:
            if not x_api_key:
                raise HTTPException(status_code=401, detail="API key required")
            
            api_key = api_key_crud.get_api_key_by_key(db, x_api_key)
            if not api_key or not api_key.is_active:
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Get model info
        model = model_crud.get_model(db, endpoint.ml_model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Prepare task data
        task_data = {
            "task_id": task_id,
            "model_id": model.id,
            "model_path": model.path,
            "framework": model.framework,  # 모델의 framework 사용
            "model_type": model.type,  # classification, regression 등 모델 타입
            "input_data": request_data
        }
        
        # Send task to Celery
        process_inference.delay(task_data)
        
        # Store task status in Redis
        redis = get_redis()
        redis.hset(
            f"task:{task_id}",
            mapping={
                "status": "pending",
                "endpoint_id": endpoint.id,
                "model_id": model.id
            }
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Inference request submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{task_id}")
async def get_inference_result(task_id: str):
    """Get inference result by task ID."""
    try:
        redis = get_redis()
        
        # Get task status
        task_status = redis.hgetall(f"task:{task_id}")
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get task result
        result = redis.get(f"task_result:{task_id}")
        if result:
            return json.loads(result)
        
        # If no result yet, return current status
        return {
            "task_id": task_id,
            "status": task_status.get(b"status", b"pending").decode(),
            "message": "Task is still processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inference result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
