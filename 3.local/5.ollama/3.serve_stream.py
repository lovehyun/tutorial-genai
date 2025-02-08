import requests
import json

url = "http://localhost:11434/api/chat"
data = {
    "model": "mistral",
    "messages": [{"role": "user", "content": "안녕?"}]
}

# 스트리밍 요청
response = requests.post(url, json=data, stream=True)

# 응답을 한 줄씩 처리
for line in response.iter_lines():
    if line:  # 빈 줄 무시
        try:
            json_response = json.loads(line)
            print(json_response["message"]["content"], end="", flush=True)
        except requests.exceptions.JSONDecodeError:
            print("\nJSON 디코딩 오류 발생! 응답 내용:", line.decode("utf-8"))
