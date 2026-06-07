"""
(3) 멀티 턴 대화 — ollama 파이썬 SDK 방식 (대화 히스토리 누적)
같은 예제의 REST 버전과 비교: ../6.ollama1_restapi/3.multiturn.py
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama

MODEL = "qwen2.5:1.5b"

# 이전 대화를 messages 에 직접 누적 → 맥락 유지 (REST 버전과 누적 로직 동일)
messages = [{"role": "system", "content": "간결히 답하세요."}]
for q in ["대한민국의 수도는?", "거기 인구는 대략 얼마야?"]:
    messages.append({"role": "user", "content": q})
    reply = ollama.chat(model=MODEL, messages=messages)["message"]["content"]
    print(f"Q: {q}\nA: {reply}\n")
    messages.append({"role": "assistant", "content": reply})

# REST 와 차이는 호출 한 줄(ollama.chat vs requests.post)뿐 — 멀티턴 원리는 같다.
