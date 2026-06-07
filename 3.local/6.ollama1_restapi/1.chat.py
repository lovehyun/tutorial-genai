"""
(1) 기본 채팅 — REST API 방식 (requests 로 직접 HTTP 호출)
같은 예제의 SDK 버전과 비교: ../6.ollama2_sdk/1.chat.py
준비: ollama pull qwen2.5:1.5b   (어떤 모델이든 가능)
"""
import requests

MODEL = "qwen2.5:1.5b"

# [REST] 엔드포인트 URL + JSON 바디를 직접 구성해 POST
resp = requests.post("http://localhost:11434/api/chat", json={
    "model": MODEL,
    "messages": [{"role": "user", "content": "파이썬의 장점 3가지를 알려줘."}],
    "stream": False,
})
print(resp.json()["message"]["content"])

# REST 방식의 의미:
#   - URL(/api/chat)·JSON 구조를 직접 다룬다 → 언어 불문(curl, JS 등)으로 동일 호출 가능
#   - 저수준이라 원리가 다 드러난다. 같은 일을 SDK 로 하면 훨씬 짧다(2.sdk 비교)
