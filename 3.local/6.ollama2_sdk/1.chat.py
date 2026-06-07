"""
(1) 기본 채팅 — ollama 파이썬 SDK 방식
같은 예제의 REST 버전과 비교: ../6.ollama1_restapi/1.chat.py
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama

MODEL = "qwen2.5:1.5b"

# [SDK] URL/JSON 없이 함수 한 번 — REST 버전과 똑같은 결과를 더 간단하게
resp = ollama.chat(model=MODEL, messages=[
    {"role": "user", "content": "파이썬의 장점 3가지를 알려줘."}
])
print(resp["message"]["content"])

# SDK 방식의 의미:
#   - requests/URL/json.loads 가 사라짐 → 코드가 짧고 읽기 쉽다
#   - 내부적으론 REST(/api/chat)를 호출하지만 그 세부를 라이브러리가 감춰준다
#   - 파이썬에서 ollama 를 쓸 땐 보통 이 방식이 가장 편하다
