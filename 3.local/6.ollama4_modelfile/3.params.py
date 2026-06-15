"""
(3) PARAMETER 가 답에 미치는 영향 — temperature 비교
    같은 베이스/질문에 temperature 만 다르게 내장한 두 모델을 만들어 비교한다.
      낮음(0.1) → 일관적·보수적   |   높음(1.0) → 다양·창의적

전제: ollama pull qwen3.5:4b
실행: python 3.params.py
"""
import ollama

BASE = "qwen3.5:4b"
PROMPT = "고양이를 주제로 짧은 4행시를 지어줘."

variants = {
    "qwen-temp-low":  0.1,
    "qwen-temp-high": 1.0,
}

# temperature 만 다른 두 커스텀 모델을 만든다 (설정만 바꾸므로 즉시 생성).
for name, temp in variants.items():
    ollama.create(model=name, from_=BASE, parameters={"temperature": temp})

# 각 모델에 두 번씩 물어 '얼마나 매번 달라지는지'를 본다.
for name, temp in variants.items():
    print("=" * 60)
    print(f"[{name}]  temperature={temp}")
    print("=" * 60)
    for i in (1, 2):
        resp = ollama.chat(model=name, messages=[{"role": "user", "content": PROMPT}])
        print(f"--- {i}회차 ---\n{resp['message']['content']}\n")

# 관찰 포인트:
#   - low:  1회차와 2회차가 비슷하다 (재현성↑).
#   - high: 회차마다 표현이 크게 달라진다 (창의성↑, 불안정성↑).
#
# 정리:  for n in qwen-temp-low qwen-temp-high; do ollama rm $n; done
