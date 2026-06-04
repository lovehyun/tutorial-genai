"""
9.3_parallelization_eg3.py - Parallelization: LLM-as-Judge 쌍대 비교(Pairwise) 토너먼트

eg2(단일 점수)의 약점: '절대 점수'는 캘리브레이션이 흔들리고 인플레이션이 있다(다 후하게).
→ LLM은 "A vs B 중 뭐가 더 나아?"라는 '상대 비교'를 절대 점수보다 훨씬 잘한다(MT-Bench 등 연구).

이 예제: 후보들을 둘씩 맞붙여(round-robin) 승점을 쌓고 최고를 고른다.

핵심 보정 — 위치 편향(position bias):
  LLM은 먼저(1번) 또는 나중(2번) 위치에 치우치는 경향이 있다.
  → 같은 쌍을 '순서를 바꿔' 두 번 비교한다.
    · 모델이 항상 1번을 선호하면 → (X,Y)에선 X승, (Y,X)에선 Y승 → 1승1패로 상쇄(무승부 효과).
    · 모델이 진짜로 X를 선호하면 → 두 순서 모두 X승 → X가 2점.

※ 빠르고 간단한 '단일 점수' 버전은 9.3_parallelization_eg2.py (같은 후보 데이터로 비교해 보세요).
"""

from itertools import combinations
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

print("=" * 60)
print("Parallelization (3) — LLM-as-Judge: 쌍대 비교(Pairwise) 토너먼트")
print("=" * 60)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── 비교 결과 스키마: 근거를 먼저, 그다음 승자(1/2/tie) ──
class Comparison(BaseModel):
    reasoning: str = Field(description="어느 쪽이 더 나은지 판단한 근거 (winner 전에 작성)")
    winner: Literal["1", "2", "tie"] = Field(description="더 나은 번역: '1'(첫 번째)·'2'(두 번째)·'tie'")


compare_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 번역 품질 평가자입니다. 두 번역 중 어느 쪽이 더 나은지 고르세요.\n"
     "정확성·문맥 적합성 / 어휘·표현력 / 자연스러움을 종합 고려하세요.\n"
     "근거(reasoning)를 먼저 쓰고, winner 를 '1'·'2'·'tie' 중 하나로 답하세요."),
    ("user", "원문(영어): {original}\n\n[1번] {cand1}\n[2번] {cand2}"),
])
comparator = compare_prompt | llm.with_structured_output(Comparison)


# ── 평가 대상: eg2와 동일한 후보 3개 ──
original = "The early bird catches the worm, but the second mouse gets the cheese."
candidates = {
    "A": "일찍 일어나는 새가 벌레를 잡지만, 두 번째 쥐가 치즈를 얻는다.",
    "B": "이른 새는 벌레를 잡고, 두 번째 마우스는 치즈를 가져간다.",
    "C": "부지런한 새가 벌레를 잡지만, 정작 이득은 한 박자 늦은 쪽이 챙긴다.",
}
names = list(candidates)

print(f"원문: {original}\n")

# ── 모든 쌍을 '양 방향'으로 비교할 작업 목록 (위치 편향 상쇄) ──
#    후보 N개 → 쌍 N(N-1)/2 개 × 2(순서) = N(N-1) 비교. (여기선 3×2=6)
jobs = []
for x, y in combinations(names, 2):
    jobs.append((x, y))   # x가 1번
    jobs.append((y, x))   # 순서 swap: y가 1번

# ── 비교들을 병렬 실행 (팬아웃) = Parallelization ──
inputs = [{"original": original, "cand1": candidates[a], "cand2": candidates[b]} for a, b in jobs]
results = comparator.batch(inputs)

# ── 승점 집계: 승=1, 무=0.5 ──
points = {n: 0.0 for n in names}
print("쌍대 비교 결과 (순서 swap 포함):")
for (left, right), r in zip(jobs, results):
    if r.winner == "1":
        points[left] += 1.0
        outcome = f"{left} 승"
    elif r.winner == "2":
        points[right] += 1.0
        outcome = f"{right} 승"
    else:
        points[left] += 0.5
        points[right] += 0.5
        outcome = "무승부"
    print(f"  [{left} vs {right}] → {outcome}")

# ── 승점 순위 → 최고 선택 (팬인) ──
ranking = sorted(points.items(), key=lambda kv: kv[1], reverse=True)
print("\n승점 합계:")
for n, p in ranking:
    print(f"  {n}: {p}점   ({candidates[n]})")
print(f"\n최종 선택: {ranking[0][0]} ({ranking[0][1]}점)")

print("\n" + "=" * 60)
print("설명:")
print("1. Pairwise: 절대 점수 대신 'A vs B' 상대 비교 → LLM이 더 잘하고 순위 신뢰도가 높다.")
print("2. 위치 편향 보정: 같은 쌍을 순서 바꿔 두 번 → 위치만 보고 고르면 1승1패로 상쇄된다.")
print("3. Round-robin 승점으로 순위. 비교들을 batch로 병렬 실행 = Parallelization.")
print("4. 비용: 후보 N개면 N(N-1)회 비교(양방향). eg2(단일 점수, N회)보다 비싸지만 순위가 더 견고하다.")
print("\n적합한 사용 사례: 최종 후보 선택(랭킹), 모델/프롬프트 A·B 테스트, 리더보드 평가")
