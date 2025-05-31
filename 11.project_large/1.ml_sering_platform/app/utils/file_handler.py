# app/utils/file_handler.py
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

def validate_model_file(file: UploadFile) -> bool:
    """Validate uploaded model file"""
    try:
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.h5', '.pkl', '.pt', '.pth', '.onnx']:
            logger.warning(f"Invalid file extension: {file_ext}")
            return False
        
        # Check file size (approximate)
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            file.file.seek(0, 2)  # Seek to end
            size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if size > settings.MAX_UPLOAD_SIZE:  # Convert MB to bytes
                logger.warning(f"File too large: {size / (1024*1024):.2f}MB")
                return False
        
        logger.debug(f"File validation passed: {file.filename}")
        return True
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return False

def save_model_file(file: UploadFile, user_id: int, model_id: int) -> tuple[str, float]:
    """
    Save uploaded model file
    Returns: (file_path, file_size_mb)
    """
    try:
        # Create user directory
        user_dir = os.path.join(settings.UPLOAD_DIR, "models", f"user_{user_id}")
        model_dir = os.path.join(user_dir, f"model_{model_id}")
        os.makedirs(model_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(model_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        logger.info(f"Model file saved: {file_path} ({file_size_mb:.2f}MB)")
        return file_path, file_size_mb
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

def delete_model_file(file_path: str) -> bool:
    """Delete model file"""
    try:
        if os.path.exists(file_path):
            # Delete file
            os.remove(file_path)
            
            # Try to remove parent directory if empty
            parent_dir = os.path.dirname(file_path)
            try:
                os.rmdir(parent_dir)
            except OSError:
                pass  # Directory not empty
            
            logger.info(f"Model file deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        return False
