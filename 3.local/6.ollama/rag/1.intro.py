# ollama run qwen2.5:1.5b
# pip install requests

import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:1.5b",
        "prompt": "안녕하세요! 자기소개를 해주세요.",
        "stream": False
    }
)

print(response.json()["response"])
