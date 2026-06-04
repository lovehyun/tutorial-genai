"""
9.3_parallelization.py - Parallelization 패턴

이 파일은 Anthropic의 Agentic 디자인 패턴 중 'Parallelization'을 구현합니다.
하나의 입력을 여러 LLM 호출로 동시에 처리(팬아웃)하고 결과를 종합(팬인)합니다.
투표(Voting) 패턴도 함께 구현하여 다수결 기반 의사결정을 보여줍니다.

예제 1: 제품 리뷰를 3가지 관점에서 동시 분석 → 종합
예제 2: 번역 품질 평가 — 3명의 평가자가 독립 투표

- Self-Consistency — 같은 프롬프트, N번 샘플링, 다수결. 수학·정답형처럼 "답이 정확히 일치"하는 경우. ← 질문하신 그것
- Universal Self-Consistency (USC) — 자유 서술처럼 다수결로 못 셀 때, LLM이 "가장 일관된 답"을 직접 고르게 함
- LLM-as-a-Judge — 후보들을 LLM 심판이 채점/선택 (Best-of-N과 결합)
- Mixture-of-Agents (MoA) — 서로 다른 여러 모델이 답을 내고 aggregator가 종합
- (넓게는 그냥 ensemble / majority voting)
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

print("=" * 60)
print("Agentic 패턴 3: Parallelization (팬아웃/팬인 + 투표)")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()

# ============================================================
# 예제 1: 팬아웃/팬인 — 다관점 분석
# ============================================================
print("\n[예제 1] 팬아웃/팬인: 제품 리뷰 다관점 분석")
print("-" * 50)

# 3가지 관점의 분석 체인
sentiment_prompt = ChatPromptTemplate.from_template(
    "다음 리뷰의 감성(긍정/부정/중립)을 분석하고 근거를 설명해주세요.\n\n리뷰: {review}"
)
feature_prompt = ChatPromptTemplate.from_template(
    "다음 리뷰에서 언급된 제품 기능과 각 기능에 대한 평가를 추출해주세요.\n\n리뷰: {review}"
)
action_prompt = ChatPromptTemplate.from_template(
    "다음 리뷰를 바탕으로 제품 개선을 위한 구체적인 제안 사항을 정리해주세요.\n\n리뷰: {review}"
)

# RunnableParallel로 3개 체인을 동시 실행 (팬아웃)
parallel_analysis = RunnableParallel(
    sentiment=sentiment_prompt | llm | parser,
    features=feature_prompt | llm | parser,
    actions=action_prompt | llm | parser,
)

# 종합 체인 (팬인)
synthesis_prompt = ChatPromptTemplate.from_template(
    """다음 3가지 분석 결과를 종합하여 최종 리뷰 분석 보고서를 작성해주세요.

감성 분석:
{sentiment}

기능 분석:
{features}

개선 제안:
{actions}

종합 보고서 (3~5줄):"""
)
synthesis_chain = synthesis_prompt | llm | parser

# 팬아웃/팬인 파이프라인 실행
review = "이 노트북은 화면이 선명하고 키보드 타건감이 좋습니다. 하지만 배터리가 3시간밖에 안 가고, 팬 소음이 심합니다. 가격 대비 성능은 괜찮은 편입니다."

print(f"리뷰: {review}\n")
print("3가지 관점에서 동시 분석 중...")
analysis_results = parallel_analysis.invoke({"review": review})

for key, value in analysis_results.items():
    print(f"\n[{key}] {value[:150]}...")

print("\n종합 보고서 생성 중...")
final_report = synthesis_chain.invoke(analysis_results)
print(f"\n종합 보고서:\n{final_report}")

# ============================================================
# 예제 2: 투표 패턴 — 다수결 의사결정
# ============================================================
print("\n" + "=" * 60)
print("[예제 2] 투표 패턴: 번역 품질 평가")
print("-" * 50)

vote_prompt = ChatPromptTemplate.from_template(
    """당신은 번역 품질 평가자입니다. 다음 번역의 품질을 평가해주세요.

원문 (영어): {original}
번역 (한국어): {translation}

'GOOD' 또는 'BAD'로만 답하세요."""
)

# 3명의 독립 평가자 (temperature를 다르게 설정하여 다양성 확보)
voter1 = vote_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.0) | parser
voter2 = vote_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.5) | parser
voter3 = vote_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=1.0) | parser

voting_panel = RunnableParallel(
    voter1=voter1,
    voter2=voter2,
    voter3=voter3,
)

# 투표 실행 및 다수결 집계
vote_input = {
    "original": "The quick brown fox jumps over the lazy dog.",
    "translation": "빠른 갈색 여우가 게으른 개를 뛰어넘습니다.",
}

print(f"원문: {vote_input['original']}")
print(f"번역: {vote_input['translation']}\n")

votes = voting_panel.invoke(vote_input)
print("투표 결과:")
for voter, vote in votes.items():
    print(f"  {voter}: {vote.strip()}")

# 다수결 집계
good_count = sum(1 for v in votes.values() if "GOOD" in v.upper())
bad_count = sum(1 for v in votes.values() if "BAD" in v.upper())
final_verdict = "GOOD" if good_count > bad_count else "BAD"
print(f"\n최종 판정 (다수결): {final_verdict} (GOOD: {good_count}, BAD: {bad_count})")

print("\n" + "=" * 60)
print("설명:")
print("1. Parallelization은 하나의 입력을 여러 LLM이 동시에 처리하는 패턴입니다.")
print("2. 팬아웃/팬인: 서로 다른 관점으로 분석 후 결과를 종합합니다.")
print("3. 투표: 여러 LLM이 독립적으로 판단하고 다수결로 최종 결정합니다.")
print("4. RunnableParallel을 사용하면 LangChain이 자동으로 병렬 실행합니다.")
print("\n적합한 사용 사례: 다관점 분석, 품질 평가, 콘텐츠 모더레이션, 앙상블 판단")
