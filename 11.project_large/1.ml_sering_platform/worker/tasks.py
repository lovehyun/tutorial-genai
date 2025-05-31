# worker/tasks.py
from celery import current_task, shared_task
from celery.exceptions import Retry
import time
import json
import logging
from typing import Dict, Any
import redis
from .celery_app import celery_app
from .model_manager.pytorch_manager import PyTorchModelManager
from .model_manager.transformers_manager import TransformersModelManager
from .model_manager.sklearn_manager import SklearnModelManager
from .inference.text_inference import TextInferenceEngine
from .inference.sklearn_inference import SklearnInferenceEngine
from .utils.model_loader import ModelLoader
from .utils.gpu_monitor import GPUMonitor
import sys
import os
import joblib
import pickle
import numpy as np
from datetime import datetime

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.crud import model_crud, endpoint_crud

logger = logging.getLogger(__name__)

# Global model managers (one per framework)
pytorch_manager = PyTorchModelManager()
transformers_manager = TransformersModelManager()
sklearn_manager = SklearnModelManager()

# Global inference engines
text_engine = TextInferenceEngine()
sklearn_engine = SklearnInferenceEngine()

# Redis client for storing results
redis_client = redis.from_url(settings.REDIS_URL)

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super(NumpyEncoder, self).default(obj)

def convert_numpy_types(obj):
    """Convert numpy types to Python native types"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

@celery_app.task(bind=True, max_retries=3)
def process_inference(self, task_data: Dict[str, Any]):
    """Process ML inference request"""
    task_id = task_data.get('task_id')
    
    try:
        logger.info(f"Processing inference task: {task_id}")
        start_time = time.time()
        
        # Log resource usage before processing
        GPUMonitor.log_resource_usage()
        
        # Extract task data
        model_id = task_data['model_id']
        model_path = task_data['model_path']
        framework = task_data.get('framework', 'sklearn').lower()  # Default to sklearn
        model_type = task_data.get('model_type', 'classification').lower()
        input_data = task_data['input_data']
        parameters = task_data.get('parameters', {})
        
        # Update task status
        redis_client.setex(
            f"task_status:{task_id}",
            3600,
            json.dumps({"status": "processing", "started_at": time.time()})
        )
        
        # Select appropriate model manager and inference engine
        if framework == 'sklearn':
            model_manager = sklearn_manager
            inference_engine = sklearn_engine
        elif framework == 'transformers':
            model_manager = transformers_manager
            inference_engine = text_engine
        else:
            model_manager = pytorch_manager
            inference_engine = text_engine if text_engine.can_handle(framework, model_type) else None
        
        # Load model
        model = model_manager.get_model(model_id, model_path, {
            'framework': framework,
            'model_type': model_type
        })
        
        # Process inference
        if inference_engine:
            result = inference_engine.process(model_manager, input_data, parameters)
        else:
            result = model_manager.predict(input_data, parameters)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare final result
        final_result = {
            "status": "completed",
            "result": result,
            "processing_time": processing_time,
            "model_id": model_id,
            "framework": framework,
            "completed_at": time.time()
        }
        
        # Convert numpy types to Python native types
        final_result = convert_numpy_types(final_result)
        
        # Store result in Redis
        redis_client.setex(
            f"task_result:{task_id}",
            3600,  # 1 hour expiry
            json.dumps(final_result)
        )
        
        # Update task status
        redis_client.setex(
            f"task_status:{task_id}",
            3600,
            json.dumps({"status": "completed", "completed_at": time.time()})
        )
        
        logger.info(f"Inference task completed: {task_id} ({processing_time:.2f}s)")
        
        # Log resource usage after processing
        GPUMonitor.log_resource_usage()
        
        return final_result
        
    except Exception as exc:
        logger.error(f"Inference task failed: {task_id} - {exc}")
        
        # Store error result
        error_result = {
            "status": "failed",
            "error": str(exc),
            "failed_at": time.time()}
        
        redis_client.setex(
            f"task_result:{task_id}",
            3600,
            json.dumps(error_result)
        )
        
        redis_client.setex(
            f"task_status:{task_id}",
            3600,
            json.dumps({"status": "failed", "failed_at": time.time()})
        )
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task: {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60, exc=exc)
        
        raise exc

@celery_app.task
def cleanup_models():
    """Cleanup idle models to free GPU memory"""
    logger.info("Running model cleanup task")
    
    try:
        # Cleanup PyTorch models
        pytorch_cleaned = pytorch_manager.cleanup_if_idle()
        if pytorch_cleaned:
            logger.info("PyTorch model cleaned up")
        
        # Cleanup Transformers models
        transformers_cleaned = transformers_manager.cleanup_if_idle()
        if transformers_cleaned:
            logger.info("Transformers model cleaned up")
        
        # Log resource usage after cleanup
        GPUMonitor.log_resource_usage()
        
        return {
            "pytorch_cleaned": pytorch_cleaned,
            "transformers_cleaned": transformers_cleaned,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Model cleanup failed: {e}")
        return {"error": str(e)}

@celery_app.task
def health_check():
    """Worker health check task"""
    try:
        gpu_stats = GPUMonitor.get_gpu_stats()
        sys_stats = GPUMonitor.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "gpu_stats": gpu_stats,
            "system_stats": sys_stats,
            "active_models": {
                "pytorch": pytorch_manager.current_model_id,
                "transformers": transformers_manager.current_model_id
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# Periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-models': {
        'task': 'worker.tasks.cleanup_models',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'health-check': {
        'task': 'worker.tasks.health_check',
        'schedule': crontab(minute='*/5'),   # Every 5 minutes
    },
}
