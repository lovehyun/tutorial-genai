"""
(3) 멀티 턴 대화 — REST API 방식 (대화 히스토리 누적)
같은 예제의 SDK 버전과 비교: ../6.ollama2_sdk/3.multiturn.py
준비: ollama pull qwen2.5:1.5b
"""
import requests

MODEL = "qwen2.5:1.5b"


def chat(messages):
    r = requests.post("http://localhost:11434/api/chat",
                      json={"model": MODEL, "messages": messages, "stream": False})
    return r.json()["message"]["content"]


# 이전 대화를 messages 에 직접 누적 → 맥락 유지 (서버는 상태를 기억하지 않음)
messages = [{"role": "system", "content": "간결히 답하세요."}]
for q in ["대한민국의 수도는?", "거기 인구는 대략 얼마야?"]:
    messages.append({"role": "user", "content": q})
    reply = chat(messages)
    print(f"Q: {q}\nA: {reply}\n")
    messages.append({"role": "assistant", "content": reply})

# REST 방식: chat() 헬퍼로 매번 POST. SDK 버전과 messages 누적 로직은 동일.
