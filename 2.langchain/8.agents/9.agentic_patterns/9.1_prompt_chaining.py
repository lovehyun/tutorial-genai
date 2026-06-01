"""
9.1_prompt_chaining.py - Prompt Chaining 패턴

이 파일은 Anthropic의 Agentic 디자인 패턴 중 'Prompt Chaining'을 구현합니다.
여러 LLM 호출을 순차적으로 연결하여 복잡한 작업을 단계별로 처리합니다.
각 단계 사이에 게이트(검증) 로직을 넣어 품질을 보장할 수 있습니다.

예제: 주제 리서치 → 게이트 검증 → 분석 → 보고서 생성
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

print("=" * 60)
print("Agentic 패턴 1: Prompt Chaining (순차 파이프라인)")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = StrOutputParser()

# ============================================================
# 1단계: 주제 리서치 — 핵심 정보 수집
# ============================================================
research_prompt = ChatPromptTemplate.from_template(
    "다음 주제에 대해 핵심 사실 5가지를 간결하게 정리해주세요.\n\n주제: {topic}"
)
research_chain = research_prompt | llm | parser

# ============================================================
# 2단계: 게이트 검증 — 리서치 결과 품질 확인
# ============================================================
gate_prompt = ChatPromptTemplate.from_template(
    """다음 리서치 결과를 평가해주세요.

리서치 결과:
{research}

평가 기준:
1. 사실 5가지가 포함되어 있는가?
2. 각 사실이 구체적이고 검증 가능한가?
3. 주제와 관련이 있는가?

'PASS' 또는 'FAIL'로만 답하고, FAIL인 경우 이유를 한 줄로 설명해주세요."""
)
gate_chain = gate_prompt | llm | parser

# ============================================================
# 3단계: 분석 — 리서치 결과 심층 분석
# ============================================================
analysis_prompt = ChatPromptTemplate.from_template(
    """다음 리서치 결과를 바탕으로 심층 분석을 작성해주세요.

리서치 결과:
{research}

다음을 포함해주세요:
- 핵심 트렌드 또는 패턴
- 시사점
- 향후 전망"""
)
analysis_chain = analysis_prompt | llm | parser

# ============================================================
# 4단계: 보고서 생성 — 최종 요약 보고서
# ============================================================
report_prompt = ChatPromptTemplate.from_template(
    """다음 리서치와 분석을 바탕으로 간결한 보고서를 작성해주세요.

리서치:
{research}

분석:
{analysis}

형식: 제목, 요약(3줄), 핵심 발견사항, 결론"""
)
report_chain = report_prompt | llm | parser


# ============================================================
# 파이프라인 실행
# ============================================================
def run_chaining_pipeline(topic: str) -> str:
    """Prompt Chaining 파이프라인을 실행합니다."""

    # 1단계: 리서치
    print("\n[1단계] 리서치 수행 중...")
    research = research_chain.invoke({"topic": topic})
    print(f"리서치 결과:\n{research[:200]}...")

    # 2단계: 게이트 검증
    print("\n[2단계] 게이트 검증 중...")
    gate_result = gate_chain.invoke({"research": research})
    print(f"게이트 결과: {gate_result}")

    if "FAIL" in gate_result.upper():
        print("게이트 검증 실패! 리서치를 재수행합니다...")
        research = research_chain.invoke({"topic": topic})
        print(f"재수행 리서치 결과:\n{research[:200]}...")

    # 3단계: 분석
    print("\n[3단계] 분석 수행 중...")
    analysis = analysis_chain.invoke({"research": research})
    print(f"분석 결과:\n{analysis[:200]}...")

    # 4단계: 보고서 생성
    print("\n[4단계] 보고서 생성 중...")
    report = report_chain.invoke({"research": research, "analysis": analysis})

    return report


# 실행
topic = "2025년 생성형 AI 시장 동향"
print(f"\n주제: {topic}")
result = run_chaining_pipeline(topic)

print("\n" + "=" * 60)
print("최종 보고서:")
print("=" * 60)
print(result)

print("\n" + "=" * 60)
print("설명:")
print("1. Prompt Chaining은 복잡한 작업을 여러 단계로 분해하여 순차적으로 처리합니다.")
print("2. 각 단계의 출력이 다음 단계의 입력이 됩니다 (리서치 → 분석 → 보고서).")
print("3. 게이트(Gate) 검증을 통해 중간 결과의 품질을 확인하고, 실패 시 재시도합니다.")
print("4. LCEL 체인을 단계별로 분리하여 각 단계를 독립적으로 테스트할 수 있습니다.")
print("\n적합한 사용 사례: 문서 생성, 데이터 처리 파이프라인, 단계별 검증이 필요한 작업")
