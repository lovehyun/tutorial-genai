# worker/model_manager/base_manager.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging
import threading
import gc

logger = logging.getLogger(__name__)

class BaseModelManager(ABC):
    """Base class for model managers"""
    
    def __init__(self, max_idle_time: int = 1800):  # 30 minutes
        self.current_model = None
        self.current_model_id = None
        self.model_info = {}
        self.last_used = None
        self.max_idle_time = max_idle_time
        self.lock = threading.Lock()
        
        logger.info(f"Initialized {self.__class__.__name__} with {max_idle_time}s idle time")
    
    @abstractmethod
    def load_model(self, model_path: str, model_info: Dict[str, Any]) -> Any:
        """Load model from file"""
        pass
    
    @abstractmethod
    def unload_model(self) -> bool:
        """Unload current model"""
        pass
    
    @abstractmethod
    def predict(self, input_data: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction"""
        pass
    
    def get_model(self, model_id: int, model_path: str, model_info: Dict[str, Any]) -> Any:
        """Get model, loading if necessary"""
        with self.lock:
            try:
                # Check if we need to load a different model
                if self.current_model_id != model_id:
                    logger.info(f"Loading new model: {model_id}")
                    
                    # Unload current model if exists
                    if self.current_model is not None:
                        self.unload_model()
                    
                    # Load new model
                    self.current_model = self.load_model(model_path, model_info)
                    self.current_model_id = model_id
                    self.model_info = model_info
                    
                    logger.info(f"Model {model_id} loaded successfully")
                
                # Update last used time
                self.last_used = time.time()
                return self.current_model
                
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                self.current_model = None
                self.current_model_id = None
                raise
    
    def should_unload(self) -> bool:
        """Check if model should be unloaded due to idle time"""
        if self.last_used is None or self.current_model is None:
            return False
        
        return (time.time() - self.last_used) > self.max_idle_time
    
    def cleanup_if_idle(self) -> bool:
        """Cleanup model if idle for too long"""
        if self.should_unload():
            logger.info(f"Unloading idle model: {self.current_model_id}")
            return self.unload_model()
        return False
