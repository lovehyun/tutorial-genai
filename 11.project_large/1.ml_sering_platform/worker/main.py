# worker/main.py
"""
Worker entry point
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.celery_app import celery_app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Celery worker")
    celery_app.start()
