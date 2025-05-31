# app/services/inference_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
import logging
import time
from typing import Dict, Any, Optional
from ..db.models.user import User
from ..db.models.model import Model
from ..db.crud.model_crud import ModelCRUD
from ..schemas.inference import InferenceRequest, InferenceResponse, InferenceResult
from ..core.config import settings
from ..utils.model_loader import load_model, run_inference, predict
from ..core.redis_client import get_redis
import joblib
import numpy as np
import json
import uuid
from ..db.models.endpoint import Endpoint

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = ModelCRUD(db)
        self._model_cache = {}
        self.redis = get_redis()
    
    async def submit_inference(self, request: Dict[str, Any], background_tasks) -> Dict[str, Any]:
        """Submit inference request to queue"""
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Prepare task data
            task_data = {
                "task_id": task_id,
                "model_id": request.model_id,
                "input_data": request.input_data
            }
            
            # Add task to Redis queue
            self.redis.lpush("inference_tasks", json.dumps(task_data))
            
            # Store task status
            self.redis.hset(
                f"task:{task_id}",
                mapping={
                    "status": "pending",
                    "model_id": request.model_id
                }
            )
            
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Inference task submitted successfully"
            }

        except Exception as e:
            logger.error(f"Error submitting inference task: {str(e)}")
            raise

    async def get_inference_result(self, task_id: str) -> Dict[str, Any]:
        """Get inference result for a task"""
        try:
            task_data = self.redis.hgetall(f"task:{task_id}")
            
            if not task_data:
                raise ValueError("Task not found")
            
            status = task_data.get(b"status", b"unknown").decode()
            
            if status == "pending":
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "message": "Task is still being processed"
                }
            elif status == "completed":
                result = json.loads(task_data.get(b"result", b"{}").decode())
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "result": result
                }
            elif status == "failed":
                error = task_data.get(b"error", b"Unknown error").decode()
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error
                }
            else:
                return {
                    "task_id": task_id,
                    "status": status,
                    "message": "Unknown task status"
                }
                
        except Exception as e:
            logger.error(f"Error getting inference result: {str(e)}")
            raise

    async def run_inference(
        self,
        task_id: str,
        model: Model,
        input_data: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None
    ):
        """추론 실행
        
        Args:
            task_id (str): 작업 ID
            model (Model): 모델 정보
            input_data (Dict[str, Any]): 입력 데이터
            parameters (Optional[Dict[str, Any]]): 추가 파라미터
        """
        try:
            # 작업 상태 업데이트
            self.redis.hset(
                f"task:{task_id}",
                mapping={
                    "status": "processing",
                    "id": model.id,
                    "input_data": input_data
                }
            )
            
            # 모델 로드 및 추론
            start_time = time.time()
            result = predict(model, input_data)
            processing_time = time.time() - start_time
            
            # 결과 저장
            self.redis.hset(
                f"task:{task_id}",
                mapping={
                    "status": "completed",
                    "result": result,
                    "processing_time": processing_time
                }
            )
            
        except Exception as e:
            logger.error(f"Error running inference: {e}")
            # 에러 상태 저장
            self.redis.hset(
                f"task:{task_id}",
                mapping={
                    "status": "failed",
                    "error": str(e)
                }
            )

    def get_model(self, model_id: int) -> Optional[Model]:
        return self.crud.get_by_id(model_id)

    def load_model(self, model: Model) -> Any:
        if model.id in self._model_cache:
            return self._model_cache[model.id]
        
        loaded_model = load_model(model.model_path)
        self._model_cache[model.id] = loaded_model
        return loaded_model

    def predict(self, model: Model, data: Dict[str, Any]) -> Dict[str, Any]:
        loaded_model = self.load_model(model)
        return predict(loaded_model, data)

    def process_inference(self, model_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process inference request"""
        try:
            # Get model
            model = self.db.query(Model).filter(Model.id == model_id).first()
            if not model:
                raise ValueError("Model not found")
            
            # Load model
            model_path = model.file_path
            if model_path.endswith('.pkl'):
                model = joblib.load(model_path)
            else:
                raise ValueError("Unsupported model format")
            
            # Prepare input data
            input_data = np.array([list(data.values())])
            
            # Make prediction
            prediction = model.predict(input_data)
            
            return {
                "prediction": prediction.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing inference: {str(e)}")
            raise
