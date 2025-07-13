import requests

OLLAMA_HOST = "http://192.168.0.7:11434"
OLLAMA_ENDPOINT = f"{OLLAMA_HOST}/api/generate"

payload = {
    "model": "codellama:13b",  # 사용 가능한 모델 중 하나 지정
    # "prompt": "파이썬에서 파일을 읽는 방법을 알려줘.",
    "prompt": "파이썬에서 리스트를 정렬하는 방법을 알려줘.",
    "stream": False
}

response = requests.post(OLLAMA_ENDPOINT, json=payload)
data = response.json()

print("모델 응답:")
print(data.get("response", "응답 없음"))
