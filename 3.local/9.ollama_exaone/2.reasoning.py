"""
(2) 단계적 추론 — "단계별로 생각하기"(Chain-of-Thought)로 정답률 높이기
같은 문제도 '바로 답' vs '단계별로 풀고 답' 을 비교한다. (ollama SDK)

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama

MODEL = "exaone3.5:latest"


def ask(prompt, temperature=0.0):
    return ollama.generate(model=MODEL, prompt=prompt,
                           options={"temperature": temperature})["response"]


problem = ("어떤 가게에서 사과를 3개 1000원에 팝니다. "
           "내가 12개를 사고 5000원을 냈다면 거스름돈은 얼마인가요?")

# [관전 포인트] 추론을 유도하는 프롬프트가 정확도를 끌어올린다
print("=" * 55, "\n (A) 바로 답만 요구\n", "=" * 55)
print(ask(problem + " 숫자만 답하세요."))

print("\n" + "=" * 55, "\n (B) 단계별로 풀게 한 뒤 답\n", "=" * 55)
print(ask(problem + " 단계별로 차근차근 계산한 뒤 마지막에 '정답: N원' 형식으로 답하세요."))

# 학습 포인트:
#   - temperature=0 으로 결정론적 추론
#   - "단계별로 생각하라"(CoT) 는 산수/논리 문제 정확도를 크게 높인다
#   - 추론형 작업은 EXAONE 같은 instruct 모델 + CoT 프롬프트 조합이 효과적
