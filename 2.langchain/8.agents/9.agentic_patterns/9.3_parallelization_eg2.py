"""
9.3_parallelization_eg2.py - Parallelization: LLM-as-Judge 단일 점수 채점 (후보 평가 → 최고 선택)

여러 후보(번역)를 '동시에' 채점(팬아웃)하고, 점수를 모아 가장 좋은 것을 고른다(팬인).

채점 방식: 0~10 '단일 점수' — 단, 여러 지표를 '종합'해서 매긴다.
  - 이진(GOOD/BAD)은 점수 인플레이션 + 변별력 부족 → 멀쩡한 번역엔 다 GOOD 이 나온다.
  - 대신 정확성·문맥 적합성 / 어휘·표현력 / 자연스러움을 '근거(reasoning)'로 먼저 짚게 하고,
    그것을 종합한 0~10 점수 하나를 받는다 (G-Eval 스타일: '근거 → 점수' 순서).
  - 후보 간 점수 차가 생겨 '선택'이 의미 있어진다.

장점: 빠르고 간단(후보당 1회 호출), 점수가 직관적.
약점: '절대 점수'라 캘리브레이션이 흔들리고 인플레이션 경향이 남는다.
  → 순위(누가 1등인가)가 핵심이면 '쌍대 비교 토너먼트'가 더 신뢰도 높다: 9.3_parallelization_eg3.py
"""

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

print("=" * 60)
print("Parallelization (2) — LLM-as-Judge: 단일 점수(0~10) 채점 → 최고 선택")
print("=" * 60)

# 심판(judge)은 일관성이 중요 → temperature=0
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── 채점 스키마: 근거를 먼저, 그다음 '여러 지표를 종합한' 0~10 단일 점수 ──
class Evaluation(BaseModel):
    reasoning: str = Field(
        description="점수 전에 먼저 쓰는 종합 근거. 정확성·문맥 적합성, 어휘·표현력, 자연스러움을 각각 짚을 것."
    )
    score: int = Field(description="위 지표들을 종합한 번역 품질 점수 (0~10)", ge=0, le=10)


judge_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 엄격하고 일관된 번역 품질 평가자입니다. 다음 지표들을 '종합'하여 0~10 점수 하나로 채점하세요.\n"
     "반드시 점수를 매기기 전에 근거(reasoning)를 먼저 작성하세요.\n"
     "- 정확성·문맥 적합성: 원문 의미를 정확하고 문맥에 맞게 옮겼는가\n"
     "- 어휘·표현력: 적절하고 풍부한 어휘를 자연스럽게 썼는가\n"
     "- 자연스러움: 한국어로 매끄럽게 읽히는가\n"
     "척도 — 10: 원어민 수준 / 6~7: 의미는 정확하나 다소 어색 / 3 이하: 오역·비문."),
    ("user", "원문(영어): {original}\n번역(한국어): {candidate}"),
])

# with_structured_output: 모델이 Evaluation 스키마(숫자 점수)로 답하도록 강제 → 파싱 불필요
judge = judge_prompt | llm.with_structured_output(Evaluation)


# ── 평가 대상: 같은 문장의 번역 후보 3개 (품질이 일부러 다르다; eg3과 동일 데이터) ──
original = "The early bird catches the worm, but the second mouse gets the cheese."
candidates = {
    "A": "일찍 일어나는 새가 벌레를 잡지만, 두 번째 쥐가 치즈를 얻는다.",        # 정확·자연스러움
    "B": "이른 새는 벌레를 잡고, 두 번째 마우스는 치즈를 가져간다.",             # '마우스' 오역·어색
    "C": "부지런한 새가 벌레를 잡지만, 정작 이득은 한 박자 늦은 쪽이 챙긴다.",   # 매끄럽지만 원문 디테일 생략
}

print(f"원문: {original}\n")

# ── 후보들을 '동시에' 채점 (팬아웃) — batch 는 같은 체인을 여러 입력에 병렬 실행한다 ──
inputs = [{"original": original, "candidate": text} for text in candidates.values()]
results = judge.batch(inputs)

# ── 점수 집계 후 최고 선택 (팬인) ──
scored = []
for name, text, ev in zip(candidates.keys(), candidates.values(), results):
    scored.append((name, ev.score, ev))
    print(f"[{name}] {ev.score}/10 — {text}")
    print(f"     근거: {ev.reasoning}\n")

best = max(scored, key=lambda x: x[1])
print(f"최종 선택: {best[0]} ({best[1]}/10)")

print("\n" + "=" * 60)
print("설명:")
print("1. LLM-as-Judge 단일 점수: 이진(GOOD/BAD) 대신 0~10 점수 + 여러 지표 종합 → 변별력 확보.")
print("2. 점수 전에 근거를 먼저(G-Eval/CoT) → 점수가 근거에 묶여 일관·정확해진다.")
print("3. judge.batch(...)로 후보들을 병렬 채점 = Parallelization.")
print("   (eg1의 RunnableParallel='한 입력에 여러 체인', 여기 batch='한 체인에 여러 입력')")
print("4. 한계: 절대 점수는 캘리브레이션·인플레이션 약점 → 순위가 핵심이면 pairwise(eg3)가 더 신뢰도 높다.")
print("\n적합한 사용 사례: 후보 응답 선택(Best-of-N), 번역·요약 품질 평가, 빠른 1차 필터")
