"""
(2) 베이스 vs 커스텀 — '튜닝(SYSTEM)'이 실제로 동작을 바꾸는 것 눈으로 확인
    같은 질문을, 규칙 없는 베이스 모델과 SYSTEM 규칙을 내장한 커스텀 모델에 던진다.
    일부러 영어로 물어봐서, 커스텀이 규칙대로 '한국어 존댓말 + 예제'로 답하는지 본다.

전제: 먼저 커스텀 모델이 있어야 함
      python 1.create_run.py   (또는  bash build.sh)
실행: python 2.compare.py
"""
import ollama

BASE = "qwen3.5:4b"       # 규칙 없음 — 질문 언어(영어)를 그대로 따라가기 쉬움
CUSTOM = "qwen-korean"    # SYSTEM 규칙 내장 — 한국어 존댓말 + 예제 + 단계별

QUESTION = "How do I reverse a string in Python?"   # 일부러 영어로 물어본다

for model in (BASE, CUSTOM):
    print("=" * 60)
    print(f"[{model}]  같은 질문, 다른 결과")
    print("=" * 60)
    resp = ollama.chat(model=model, messages=[
        {"role": "user", "content": QUESTION}
    ])
    print(resp["message"]["content"], "\n")

# 포인트:
#   - 베이스: system 이 없으니 질문 언어(영어)를 그대로 따라가기 쉽다.
#   - 커스텀: SYSTEM 규칙 덕분에 질문이 영어여도 한국어 존댓말 + 예제로 답한다.
#   → 코드 한 줄 안 바꾸고 'Modelfile(SYSTEM)' 만으로 동작이 달라진다 = 가벼운 튜닝.
