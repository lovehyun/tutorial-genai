# tests/test_worker.py
"""
Worker tests
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os
import json

from worker.model_manager.pytorch_manager import PyTorchModelManager
from worker.model_manager.transformers_manager import TransformersModelManager
from worker.model_manager.sklearn_manager import SklearnModelManager
from worker.inference.text_inference import TextInferenceEngine
from worker.inference.sklearn_inference import SklearnInferenceEngine
from worker.utils.model_loader import ModelLoader
from worker.utils.gpu_monitor import GPUMonitor

class TestPyTorchManager:
    
    def test_init(self):
        manager = PyTorchModelManager()
        assert manager.current_model is None
        assert manager.current_model_id is None
    
    def test_simple_model_loading(self):
        """Test loading a simple PyTorch model"""
        # Create a simple model
        model = torch.nn.Linear(10, 1)
        
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
            torch.save(model, f.name)
            
            manager = PyTorchModelManager()
            loaded_model = manager.load_model(f.name, {"framework": "pytorch"})
            
            assert loaded_model is not None
            assert isinstance(loaded_model, torch.nn.Module)
            
            # Cleanup
            os.unlink(f.name)
    
    def test_prediction(self):
        """Test PyTorch model prediction"""
        model = torch.nn.Linear(10, 1)
        
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
            torch.save(model, f.name)
            
            manager = PyTorchModelManager()
            manager.get_model(1, f.name, {"framework": "pytorch"})
            
            # Test prediction
            input_data = {"data": [[1.0] * 10]}
            result = manager.predict(input_data)
            
            assert "predictions" in result
            assert result["model_type"] == "pytorch"
            
            # Cleanup
            os.unlink(f.name)

class TestSklearnManager:
    
    def test_init(self):
        manager = SklearnModelManager()
        assert manager.current_model is None
        assert manager.current_model_id is None
    
    def test_model_loading(self):
        """Test loading a scikit-learn model"""
        from sklearn.linear_model import LogisticRegression
        
        # Create a simple model
        model = LogisticRegression()
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 1, 0])
        model.fit(X, y)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            import pickle
            pickle.dump(model, f)
            
            manager = SklearnModelManager()
            loaded_model = manager.load_model(f.name, {"framework": "sklearn"})
            
            assert loaded_model is not None
            assert hasattr(loaded_model, 'predict')
            
            # Cleanup
            os.unlink(f.name)
    
    def test_prediction(self):
        """Test scikit-learn model prediction"""
        from sklearn.linear_model import LogisticRegression
        
        # Create and train a simple model
        model = LogisticRegression()
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 1, 0])
        model.fit(X, y)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            import pickle
            pickle.dump(model, f)
            
            manager = SklearnModelManager()
            manager.get_model(1, f.name, {"framework": "sklearn"})
            
            # Test prediction
            input_data = {"data": [[1, 2]]}
            result = manager.predict(input_data)
            
            assert "predictions" in result
            assert result["model_type"] == "sklearn"
            
            # Cleanup
            os.unlink(f.name)

class TestTextInferenceEngine:
    
    def test_can_handle(self):
        engine = TextInferenceEngine()
        
        assert engine.can_handle("pytorch", "text-classification")
        assert engine.can_handle("transformers", "sentiment-analysis")
        assert not engine.can_handle("tensorflow", "image-classification")

class TestSklearnInferenceEngine:
    
    def test_can_handle(self):
        engine = SklearnInferenceEngine()
        
        assert engine.can_handle("sklearn", "classification")
        assert engine.can_handle("sklearn", "regression")
        assert not engine.can_handle("pytorch", "text-classification")

class TestModelLoader:
    
    def test_detect_framework(self):
        # Test PyTorch detection
        assert ModelLoader.detect_model_framework("model.pt") == "pytorch"
        assert ModelLoader.detect_model_framework("model.pth") == "pytorch"
        
        # Test scikit-learn detection
        assert ModelLoader.detect_model_framework("model.pkl") == "sklearn"
        
        # Test with config.json (Transformers)
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            model_path = os.path.join(tmpdir, "model.bin")
            
            with open(config_path, 'w') as f:
                json.dump({"model_type": "bert"}, f)
            
            assert ModelLoader.detect_model_framework(model_path) == "transformers"

class TestGPUMonitor:
    
    def test_get_gpu_stats(self):
        stats = GPUMonitor.get_gpu_stats()
        
        assert "gpu_available" in stats
        assert "gpu_count" in stats
        assert "memory_allocated" in stats
        assert isinstance(stats["gpu_available"], bool)
    
    def test_get_system_stats(self):
        stats = GPUMonitor.get_system_stats()
        
        assert "cpu_percent" in stats
        assert "memory_percent" in stats
        assert "memory_total" in stats
        assert all(isinstance(stats[key], (int, float)) for key in stats)
