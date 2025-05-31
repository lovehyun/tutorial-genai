# worker/utils/model_loader.py
import os
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """Utility for loading model metadata and files"""
    
    @staticmethod
    def load_model_info(model_path: str) -> Dict[str, Any]:
        """Load model information from metadata files"""
        try:
            model_dir = os.path.dirname(model_path)
            info = {}
            
            # Try to load config.json (Transformers format)
            config_path = os.path.join(model_dir, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    info.update({
                        'model_type': config.get('model_type', 'unknown'),
                        'architecture': config.get('architectures', ['unknown'])[0],
                        'vocab_size': config.get('vocab_size'),
                        'hidden_size': config.get('hidden_size'),
                    })
            
            # Try to load custom metadata
            metadata_path = os.path.join(model_dir, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    info.update(metadata)
            
            logger.debug(f"Loaded model info: {info}")
            return info
            
        except Exception as e:
            logger.warning(f"Could not load model info: {e}")
            return {}
    
    @staticmethod
    def detect_model_framework(model_path: str) -> str:
        """Detect model framework from file extension and contents"""
        try:
            file_ext = os.path.splitext(model_path)[1].lower()
            model_dir = os.path.dirname(model_path)
            
            # Check for Transformers indicators
            if (os.path.exists(os.path.join(model_dir, 'config.json')) or
                os.path.exists(os.path.join(model_dir, 'tokenizer.json')) or
                file_ext == '.safetensors'):
                return 'transformers'
            
            # Check for PyTorch
            if file_ext in ['.pt', '.pth', '.bin']:
                return 'pytorch'
            
            # Default
            return 'pytorch'
            
        except Exception as e:
            logger.warning(f"Could not detect framework: {e}")
            return 'pytorch'
