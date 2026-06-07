"""
(2) 스트리밍 — ollama 파이썬 SDK 방식
같은 예제의 REST 버전과 비교: ../6.ollama1_restapi/2.streaming.py
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama

MODEL = "qwen2.5:1.5b"

# [SDK] stream=True 면 청크를 그냥 for 루프로 — NDJSON 파싱이 필요 없다
for chunk in ollama.chat(model=MODEL,
                         messages=[{"role": "user", "content": "파이썬의 장점 3가지를 알려줘."}],
                         stream=True):
    print(chunk["message"]["content"], end="", flush=True)
print()

# REST 버전과 비교: iter_lines()+json.loads 가 사라지고 for 루프 한 줄. 같은 스트리밍을 더 쉽게.
