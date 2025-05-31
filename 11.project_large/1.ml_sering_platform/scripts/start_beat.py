# scripts/start_beat.py
"""
Start Celery beat scheduler script
"""
import sys
import os
import subprocess
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_beat():
    """Start Celery beat scheduler"""
    try:
        cmd = [
            "celery", 
            "-A", "worker.celery_app", 
            "beat", 
            "--loglevel=info",
            "--hostname=beat@%h"  # Unique hostname for beat
        ]
        
        logger.info("Starting Celery beat with command: " + " ".join(cmd))
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("Beat stopped by user")
    except Exception as e:
        logger.error(f"Failed to start beat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_beat()
