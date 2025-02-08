import requests

url = "http://localhost:11434/api/chat"
data = {
    "model": "mistral",
    "messages": [{"role": "user", "content": "안녕?"}],
    "stream": False  # 스트리밍 모드 비활성화
}

response = requests.post(url, json=data)
json_response = response.json()

# 전체 응답 출력
print(json_response["message"]["content"])
