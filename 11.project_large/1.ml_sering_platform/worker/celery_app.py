# worker/celery_app.py
from celery import Celery
import os
import sys
import logging
from typing import Dict, Any
from celery.signals import after_setup_logger

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from app.core.config import settings

# Create logs directory
log_dir = os.path.join(parent_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# Configure logging for worker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'worker.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "ml_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    
    # Task routing
    task_routes={
        "worker.tasks.process_inference": {"queue": "inference_tasks"},
        "worker.tasks.cleanup_models": {"queue": "maintenance"},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time for GPU memory management
    task_acks_late=True,
    worker_disable_rate_limits=True,
    broker_connection_retry_on_startup=True,
    
    # Task settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=3600,       # 1 hour
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Queue settings
    task_default_queue='inference_tasks',
    task_queues={
        'inference_tasks': {
            'exchange': 'inference_tasks',
            'routing_key': 'inference_tasks',
        }
    }
)

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 파일 핸들러 추가
    fh = logging.FileHandler(os.path.join(log_dir, 'worker.log'))
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger.info("Celery worker app configured")
