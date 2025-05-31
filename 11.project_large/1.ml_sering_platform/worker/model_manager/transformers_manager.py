# worker/model_manager/transformers_manager.py
from transformers import AutoModel, AutoTokenizer, AutoConfig, pipeline
import torch
from typing import Dict, Any, Optional
import logging
import os
from .base_manager import BaseModelManager

logger = logging.getLogger(__name__)

class TransformersModelManager(BaseModelManager):
    """Hugging Face Transformers model manager"""
    
    def __init__(self, max_idle_time: int = 1800):
        super().__init__(max_idle_time)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.pipeline_obj = None
        logger.info(f"Transformers manager using device: {self.device}")
    
    def load_model(self, model_path: str, model_info: Dict[str, Any]) -> Any:
        """Load Transformers model"""
        try:
            logger.info(f"Loading Transformers model from: {model_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Determine model type from model_info
            model_type = model_info.get('model_type', 'auto')
            task = model_info.get('task', 'feature-extraction')
            
            # Load tokenizer if available
            try:
                model_dir = os.path.dirname(model_path)
                if os.path.exists(os.path.join(model_dir, 'tokenizer.json')) or \
                   os.path.exists(os.path.join(model_dir, 'vocab.txt')):
                    self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
                    logger.info("Tokenizer loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load tokenizer: {e}")
            
            # Load model based on file type
            if model_path.endswith('.bin') or model_path.endswith('.safetensors'):
                # Load as Transformers model
                model_dir = os.path.dirname(model_path)
                model = AutoModel.from_pretrained(model_dir, device_map="auto" if torch.cuda.is_available() else None)
                
                # Create pipeline if task is specified
                if self.tokenizer and task != 'feature-extraction':
                    self.pipeline_obj = pipeline(
                        task=task,
                        model=model,
                        tokenizer=self.tokenizer,
                        device=0 if torch.cuda.is_available() else -1
                    )
                    logger.info(f"Pipeline created for task: {task}")
            else:
                # Fallback to PyTorch loading
                model = torch.load(model_path, map_location=self.device)
            
            logger.info(f"Transformers model loaded successfully")
            
            if torch.cuda.is_available():
                logger.info(f"GPU Memory used: {torch.cuda.memory_allocated() / 1e9:.2f}GB")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load Transformers model: {e}")
            raise
    
    def unload_model(self) -> bool:
        """Unload Transformers model"""
        try:
            if self.current_model is not None:
                logger.info(f"Unloading Transformers model: {self.current_model_id}")
                
                # Clear pipeline
                if self.pipeline_obj is not None:
                    del self.pipeline_obj
                    self.pipeline_obj = None
                
                # Clear tokenizer
                if self.tokenizer is not None:
                    del self.tokenizer
                    self.tokenizer = None
                
                # Clear model
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
                
                logger.info("Transformers model unloaded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unload Transformers model: {e}")
            return False
    
    def predict(self, input_data: Dict[str, Any], parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction with Transformers model"""
        try:
            if self.current_model is None:
                raise ValueError("No model loaded")
            
            logger.debug("Making Transformers prediction")
            
            # Use pipeline if available
            if self.pipeline_obj is not None:
                text_input = input_data.get('text', input_data.get('input', ''))
                if not text_input:
                    raise ValueError("Text input required for pipeline")
                
                # Apply parameters
                kwargs = parameters or {}
                output = self.pipeline_obj(text_input, **kwargs)
                
                result = {
                    "predictions": output,
                    "model_type": "transformers",
                    "used_pipeline": True,
                    "device": str(self.device)
                }
            else:
                # Manual prediction
                if self.tokenizer is None:
                    raise ValueError("No tokenizer available for manual prediction")
                
                text_input = input_data.get('text', input_data.get('input', ''))
                if not text_input:
                    raise ValueError("Text input required")
                
                # Tokenize
                inputs = self.tokenizer(
                    text_input,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                
                # Move to device
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Forward pass
                with torch.no_grad():
                    outputs = self.current_model(**inputs)
                
                # Extract predictions
                if hasattr(outputs, 'last_hidden_state'):
                    predictions = outputs.last_hidden_state.cpu().numpy().tolist()
                elif hasattr(outputs, 'logits'):
                    predictions = outputs.logits.cpu().numpy().tolist()
                else:
                    predictions = outputs[0].cpu().numpy().tolist() if isinstance(outputs, tuple) else outputs.cpu().numpy().tolist()
                
                result = {
                    "predictions": predictions,
                    "model_type": "transformers",
                    "used_pipeline": False,
                    "device": str(self.device)
                }
            
            logger.debug("Transformers prediction completed")
            return result
            
        except Exception as e:
            logger.error(f"Transformers prediction failed: {e}")
            raise
