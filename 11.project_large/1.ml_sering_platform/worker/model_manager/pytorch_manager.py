# worker/model_manager/pytorch_manager.py
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import logging
import os
from .base_manager import BaseModelManager

logger = logging.getLogger(__name__)

class PyTorchModelManager(BaseModelManager):
    """PyTorch model manager"""
    
    def __init__(self, max_idle_time: int = 1800):
        super().__init__(max_idle_time)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"PyTorch manager using device: {self.device}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    
    def load_model(self, model_path: str, model_info: Dict[str, Any]) -> torch.nn.Module:
        """Load PyTorch model"""
        try:
            logger.info(f"Loading PyTorch model from: {model_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load model based on file extension
            if model_path.endswith(('.pt', '.pth')):
                model = torch.load(model_path, map_location=self.device)
            elif model_path.endswith('.bin'):
                # For models saved as state_dict
                model = torch.load(model_path, map_location=self.device)
                if isinstance(model, dict):
                    raise ValueError("State dict loading requires model architecture")
            else:
                raise ValueError(f"Unsupported file format: {os.path.splitext(model_path)[1]}")
            
            # Ensure model is on correct device
            if hasattr(model, 'to'):
                model = model.to(self.device)
            
            # Set to evaluation mode
            if hasattr(model, 'eval'):
                model.eval()
            
            logger.info(f"PyTorch model loaded successfully on {self.device}")
            
            if torch.cuda.is_available():
                logger.info(f"GPU Memory used: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load PyTorch model: {e}")
            raise
    
    def unload_model(self) -> bool:
        """Unload PyTorch model"""
        try:
            if self.current_model is not None:
                logger.info(f"Unloading PyTorch model: {self.current_model_id}")
                
                # Move to CPU and delete
                if hasattr(self.current_model, 'cpu'):
                    self.current_model.cpu()
                
                del self.current_model
                self.current_model = None
                self.current_model_id = None
                self.model_info = {}
                self.last_used = None
                
                # Clear GPU cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info(f"GPU Memory after cleanup: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
                
                # Force garbage collection
                import gc
                gc.collect()
                
                logger.info("PyTorch model unloaded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unload PyTorch model: {e}")
            return False
    
    def predict(self, input_data: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction with PyTorch model"""
        try:
            if self.current_model is None:
                raise ValueError("No model loaded")
            
            logger.debug("Making PyTorch prediction")
            
            # Extract input tensor
            if 'tensor' in input_data:
                # Direct tensor input
                input_tensor = torch.tensor(input_data['tensor'], device=self.device)
            elif 'data' in input_data:
                # Numeric data input
                input_tensor = torch.tensor(input_data['data'], device=self.device, dtype=torch.float32)
            else:
                raise ValueError("Invalid input format. Expected 'tensor' or 'data' key")
            
            # Ensure proper dimensions
            if input_tensor.dim() == 1:
                input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension
            
            # Make prediction
            with torch.no_grad():
                output = self.current_model(input_tensor)
            
            # Convert output to CPU and numpy
            if isinstance(output, torch.Tensor):
                output_data = output.cpu().numpy().tolist()
            elif isinstance(output, (list, tuple)):
                output_data = [o.cpu().numpy().tolist() if isinstance(o, torch.Tensor) else o for o in output]
            else:
                output_data = output
            
            result = {
                "predictions": output_data,
                "model_type": "pytorch",
                "device": str(self.device)
            }
            
            logger.debug("PyTorch prediction completed")
            return result
            
        except Exception as e:
            logger.error(f"PyTorch prediction failed: {e}")
            raise
