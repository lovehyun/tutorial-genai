# worker/inference/base_inference.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseInferenceEngine(ABC):
    """Base inference engine interface"""
    
    def __init__(self):
        self.supported_frameworks = []
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def can_handle(self, framework: str, model_type: str) -> bool:
        """Check if this engine can handle the given framework/model type"""
        pass
    
    @abstractmethod
    def process(self, model_manager, input_data: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process inference request"""
        pass
