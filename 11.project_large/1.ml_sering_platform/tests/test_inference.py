# tests/test_inference.py
"""
Test inference functionality
"""
import requests
import json
import time
import os
import tempfile
import numpy as np
from sklearn.linear_model import LogisticRegression

def create_test_model():
    """Create a test scikit-learn model"""
    model = LogisticRegression()
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([0, 1, 0])
    model.fit(X, y)
    
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        import pickle
        pickle.dump(model, f)
        return f.name

def test_full_inference_flow():
    """Test complete inference flow"""
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Register user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=user_data)
    print(f"Register: {response.status_code}")
    
    # 2. Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Login: {response.status_code}")
    
    # 3. Create API key
    api_key_data = {"name": "test_key"}
    response = requests.post(f"{base_url}/api-keys/", json=api_key_data, headers=headers)
    api_key = response.json()["key"]
    print(f"API Key created: {response.status_code}")
    
    # 4. Upload model
    model_path = create_test_model()
    model_data = {
        "name": "Test Model",
        "description": "Test scikit-learn model",
        "framework": "sklearn",
        "task_type": "classification",
        "input_type": "tabular",
        "output_type": "classification"
    }
    
    files = {
        'file': ('model.pkl', open(model_path, 'rb'), 'application/octet-stream')
    }
    
    response = requests.post(
        f"{base_url}/models/",
        data=model_data,
        files=files,
        headers=headers
    )
    
    model_id = response.json()["id"]
    print(f"Model uploaded: {response.status_code}")
    
    # Cleanup model file
    os.unlink(model_path)
    
    # 5. Test inference
    inference_headers = {"X-API-Key": api_key}
    inference_data = {
        "model_id": model_id,
        "input_data": {
            "data": [[1, 2]]
        },
        "parameters": {}
    }
    
    response = requests.post(f"{base_url}/inference/predict", 
                           json=inference_data, 
                           headers=inference_headers)
    
    if response.status_code == 200:
        task_id = response.json()["task_id"]
        print(f"Inference submitted: {task_id}")
        
        # 6. Check result
        time.sleep(5)  # Wait for processing
        response = requests.get(f"{base_url}/inference/result/{task_id}", 
                              headers=inference_headers)
        print(f"Result: {response.json()}")
    else:
        print(f"Inference failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_full_inference_flow()
