from typing import Dict, Any
from .base_inference import BaseInferenceEngine

class SklearnInferenceEngine(BaseInferenceEngine):
    """Inference engine for scikit-learn models"""
    
    def can_handle(self, framework: str, model_type: str) -> bool:
        """Check if this engine can handle the given framework and model type"""
        return framework.lower() == 'sklearn'
    
    def process(self, model_manager: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process inference request for sklearn models"""
        # For sklearn models, we can directly use the model manager's predict method
        # as it already handles all the necessary preprocessing and postprocessing
        return model_manager.predict(input_data, parameters) 