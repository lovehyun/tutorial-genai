from typing import Dict, Any, Optional
import pickle
import numpy as np
import time
from .base_manager import BaseModelManager

class SklearnModelManager(BaseModelManager):
    """Manager for scikit-learn models"""
    
    def __init__(self):
        super().__init__()
        self.current_model = None
        self.current_model_id = None
        self.model_info = None
        self.feature_names = None
        self.target_names = None
    
    def load_model(self, model_path: str, model_info: Dict[str, Any]) -> Any:
        """Load a scikit-learn model from file"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.feature_names = model_data.get('feature_names', [])
            self.target_names = model_data.get('target_names', [])
            return model_data['model']
        except Exception as e:
            raise Exception(f"Failed to load sklearn model: {str(e)}")
    
    def unload_model(self) -> None:
        """Unload the current model"""
        self.current_model = None
        self.current_model_id = None
        self.model_info = None
        self.feature_names = None
        self.target_names = None
    
    def get_model(self, model_id: str, model_path: str, model_info: Dict[str, Any]) -> Any:
        """Load and return a scikit-learn model"""
        if self.current_model_id != model_id:
            try:
                self.current_model = self.load_model(model_path, model_info)
                self.current_model_id = model_id
                self.model_info = model_info
                self.last_used = time.time()
            except Exception as e:
                raise Exception(f"Failed to load sklearn model: {str(e)}")
        
        return self.current_model
    
    def predict(self, input_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make predictions using the loaded model"""
        if not self.current_model:
            raise Exception("No model loaded")
        
        try:
            # Convert input data to numpy array
            input_array = np.array([list(input_data.values())])
            
            # Make prediction
            prediction = self.current_model.predict(input_array)
            
            # Convert prediction to list and map to target names if available
            prediction_list = prediction.tolist()
            if len(self.target_names) > 0:  # Check if target_names is not empty
                prediction_list = [self.target_names[int(pred)] for pred in prediction_list]
            
            return {
                "prediction": prediction_list,
                "feature_names": self.feature_names,
                "target_names": self.target_names
            }
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
    
    def cleanup_if_idle(self) -> bool:
        """Cleanup model if it's been idle for too long"""
        if self.current_model and time.time() - self.last_used > self.idle_timeout:
            self.unload_model()
            return True
        return False 