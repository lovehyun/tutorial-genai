"""
(5) 코드 어시스턴트 — 코드 생성 + 설명/리뷰 (ollama SDK)
EXAONE 로 간단한 코딩 보조. (전문 코드모델만큼은 아니어도 학습/보조엔 충분)

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama

MODEL = "exaone3.5:latest"


def ask(prompt, temperature=0.2):
    return ollama.chat(
        model=MODEL, options={"temperature": temperature},
        messages=[{"role": "system", "content": "당신은 친절한 파이썬 코딩 도우미입니다."},
                  {"role": "user", "content": prompt}],
    )["message"]["content"]


# 1) 코드 생성
print("=" * 55, "\n 코드 생성\n", "=" * 55)
print(ask("리스트에서 중복을 제거하고 정렬하는 파이썬 함수를 작성해줘. 코드만."))

# 2) 코드 설명/리뷰
print("\n" + "=" * 55, "\n 코드 설명\n", "=" * 55)
snippet = "result = [x**2 for x in range(10) if x % 2 == 0]"
print(ask(f"다음 파이썬 코드가 무슨 일을 하는지 한국어로 한 줄로 설명해줘:\n{snippet}"))

# 학습 포인트:
#   - 코딩 작업은 temperature 를 낮게(0.2) — 정확성 우선
#   - 시스템 프롬프트로 역할(코딩 도우미)을 고정하면 응답 형식이 안정적
#   - 더 강한 코드 생성은 코드 전용 모델(CodeLlama, Qwen2.5-Coder 등) 고려
