"""
(2) 스트리밍 — REST API 방식 (생성되는 토큰을 줄 단위로 수신)
같은 예제의 SDK 버전과 비교: ../6.ollama2_sdk/2.streaming.py
준비: ollama pull qwen2.5:1.5b
"""
import requests
import json

MODEL = "qwen2.5:1.5b"

# [REST] stream=True → 서버가 NDJSON(줄마다 부분 응답)을 흘려보낸다 → 직접 파싱
with requests.post("http://localhost:11434/api/chat",
                   json={"model": MODEL,
                         "messages": [{"role": "user", "content": "파이썬의 장점 3가지를 알려줘."}],
                         "stream": True},
                   stream=True) as r:
    for line in r.iter_lines():
        if line:
            chunk = json.loads(line)
            print(chunk.get("message", {}).get("content", ""), end="", flush=True)
            if chunk.get("done"):
                break
print()

# REST 스트리밍: iter_lines() 로 줄을 받아 매번 json.loads → content 조각 이어붙임 (수작업)
