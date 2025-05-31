# tests/performance_test.py
"""
Performance testing for the ML serving platform
"""
import asyncio
import aiohttp
import time
import statistics
import os
import tempfile
import numpy as np
from sklearn.linear_model import LogisticRegression
from concurrent.futures import ThreadPoolExecutor

class PerformanceTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_key = None
        self.model_id = None
        
    def create_test_model(self):
        """Create a test scikit-learn model"""
        model = LogisticRegression()
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 1, 0])
        model.fit(X, y)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            import pickle
            pickle.dump(model, f)
            return f.name
        
    async def setup(self):
        """Setup test environment"""
        async with aiohttp.ClientSession() as session:
            # Register and login
            user_data = {
                "username": f"perftest_{int(time.time())}",
                "email": f"perftest_{int(time.time())}@example.com",
                "password": "testpass123"
            }
            
            await session.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
            
            login_response = await session.post(f"{self.base_url}/api/v1/auth/login", json={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = (await login_response.json())["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create API key
            api_key_response = await session.post(
                f"{self.base_url}/api/v1/api-keys/",
                json={"name": "perf_test"},
                headers=headers
            )
            
            self.api_key = (await api_key_response.json())["key"]
            
            # Upload test model
            model_path = self.create_test_model()
            model_data = {
                "name": "Performance Test Model",
                "description": "Test scikit-learn model for performance testing",
                "framework": "sklearn",
                "task_type": "classification",
                "input_type": "tabular",
                "output_type": "classification"
            }
            
            data = aiohttp.FormData()
            data.add_field('file',
                         open(model_path, 'rb'),
                         filename='model.pkl',
                         content_type='application/octet-stream')
            
            for key, value in model_data.items():
                data.add_field(key, value)
            
            model_response = await session.post(
                f"{self.base_url}/api/v1/models/",
                data=data,
                headers=headers
            )
            
            self.model_id = (await model_response.json())["id"]
            
            # Cleanup model file
            os.unlink(model_path)
    
    async def test_inference_latency(self, num_requests=10):
        """Test inference latency"""
        latencies = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(num_requests):
                start_time = time.time()
                
                # Submit inference
                inference_data = {
                    "model_id": self.model_id,
                    "input_data": {"data": [[1, 2]]},
                    "parameters": {}
                }
                
                headers = {"X-API-Key": self.api_key}
                response = await session.post(
                    f"{self.base_url}/api/v1/inference/predict",
                    json=inference_data,
                    headers=headers
                )
                
                if response.status == 200:
                    task_id = (await response.json())["task_id"]
                    
                    # Wait for completion
                    while True:
                        result_response = await session.get(
                            f"{self.base_url}/api/v1/inference/result/{task_id}",
                            headers=headers
                        )
                        
                        result = await result_response.json()
                        if result["status"] in ["completed", "failed"]:
                            break
                        
                        await asyncio.sleep(0.1)
                    
                    latency = time.time() - start_time
                    latencies.append(latency)
                    print(f"Request {i+1}: {latency:.3f}s")
        
        if latencies:
            print(f"\nLatency Stats:")
            print(f"Mean: {statistics.mean(latencies):.3f}s")
            print(f"Median: {statistics.median(latencies):.3f}s")
            print(f"Min: {min(latencies):.3f}s")
            print(f"Max: {max(latencies):.3f}s")
        
        return latencies

async def main():
    tester = PerformanceTest()
    await tester.setup()
    await tester.test_inference_latency(5)

if __name__ == "__main__":
    asyncio.run(main())
