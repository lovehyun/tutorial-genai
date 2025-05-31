# worker/inference/text_inference.py
from typing import Dict, Any
import logging
from .base_inference import BaseInferenceEngine

logger = logging.getLogger(__name__)

class TextInferenceEngine(BaseInferenceEngine):
    """Text-based inference engine"""
    
    def __init__(self):
        super().__init__()
        self.supported_frameworks = ["pytorch", "transformers"]
        self.supported_tasks = [
            "text-classification", 
            "sentiment-analysis",
            "text-generation",
            "feature-extraction",
            "question-answering",
            "summarization"
        ]
    
    def can_handle(self, framework: str, model_type: str) -> bool:
        """Check if can handle text inference"""
        return (
            framework.lower() in self.supported_frameworks and
            (model_type.lower() in self.supported_tasks or "text" in model_type.lower())
        )
    
    def process(self, model_manager, input_data: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process text inference"""
        try:
            logger.debug("Processing text inference")
            
            # Validate input
            if 'text' not in input_data and 'input' not in input_data:
                raise ValueError("Text input required for text inference")
            
            # Set default parameters for text processing
            params = parameters or {}
            if 'max_length' not in params:
                params['max_length'] = 512
            if 'do_sample' not in params and 'text-generation' in str(model_manager.model_info.get('task', '')):
                params['do_sample'] = True
                params['temperature'] = 0.7
            
            # Process with model manager
            result = model_manager.predict(input_data, params)
            
            # Add processing metadata
            result['inference_type'] = 'text'
            result['input_length'] = len(input_data.get('text', input_data.get('input', '')))
            
            logger.debug("Text inference completed")
            return result
            
        except Exception as e:
            logger.error(f"Text inference failed: {e}")
            raise
