# scripts/start_worker.py
"""
Start Celery worker script
"""
import sys
import os
import subprocess
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_worker():
    """Start Celery worker"""
    try:
        cmd = [
            "celery", 
            "-A", "worker.celery_app", 
            "worker", 
            "--loglevel=info",
            "--concurrency=1",  # Single process for GPU memory management
            "--queues=inference_tasks,maintenance",
            "--hostname=worker@%h"  # Unique hostname for worker
        ]
        
        logger.info("Starting Celery worker with command: " + " ".join(cmd))
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_worker()
