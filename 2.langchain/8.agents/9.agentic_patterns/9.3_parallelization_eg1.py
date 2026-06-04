"""
9.3_parallelization_eg1.py - Parallelization: 팬아웃/팬인 (다관점 분석)

Anthropic Agentic 패턴 'Parallelization'의 두 갈래 중 (1) 팬아웃/팬인(Fan-out/Fan-in).
하나의 입력을 여러 LLM 호출로 '동시에' 처리(팬아웃)하고, 그 결과들을 하나로 종합(팬인)한다.

예제: 제품 리뷰를 3가지 관점(감성 / 기능 / 개선제안)에서 동시 분석 → 종합 보고서

※ 같은 주제의 다른 갈래(투표/다수결)는 9.3_parallelization_eg2.py 참고.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

print("=" * 60)
print("Parallelization (1) — 팬아웃/팬인: 제품 리뷰 다관점 분석")
print("=" * 60)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()

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

print("\n" + "=" * 60)
print("설명:")
print("1. 팬아웃/팬인: 하나의 입력을 서로 다른 관점의 체인들이 '동시에' 처리한다.")
print("2. RunnableParallel을 쓰면 LangChain이 3개 호출을 자동으로 병렬 실행한다.")
print("3. 결과 dict를 종합(synthesis) 체인에 넣어 하나의 보고서로 합친다(팬인).")
print("\n적합한 사용 사례: 다관점 분석, 문서 다각도 요약, 콘텐츠 모더레이션")
