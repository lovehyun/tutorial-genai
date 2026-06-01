"""
9.2_routing.py - Routing 패턴

이 파일은 Anthropic의 Agentic 디자인 패턴 중 'Routing'을 구현합니다.
LLM이 입력을 분류하고, 분류 결과에 따라 전문화된 체인으로 분기합니다.
각 분기는 서로 다른 프롬프트와 처리 로직을 가집니다.

예제: 고객 문의 → 분류(기술/결제/일반) → 전문 체인 → 응답
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

print("=" * 60)
print("Agentic 패턴 2: Routing (입력 분류 → 전문 체인 분기)")
print("=" * 60)

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# ============================================================
# 1. 분류기 (Router) — 입력을 카테고리로 분류
# ============================================================
classifier_prompt = ChatPromptTemplate.from_template(
    """다음 고객 문의를 분류해주세요. 반드시 아래 카테고리 중 하나만 출력하세요.

카테고리: technical, billing, general

고객 문의: {query}

카테고리:"""
)
classifier_chain = classifier_prompt | llm | parser

# ============================================================
# 2. 전문 체인 정의 — 카테고리별 처리
# ============================================================

# 기술 지원 체인
technical_prompt = ChatPromptTemplate.from_template(
    """당신은 기술 지원 전문가입니다. 정확하고 단계별로 문제 해결 방법을 안내해주세요.

고객 문의: {query}

기술 지원 응답:"""
)
technical_chain = technical_prompt | llm | parser

# 결제 지원 체인
billing_prompt = ChatPromptTemplate.from_template(
    """당신은 결제 및 구독 전문 상담원입니다. 정책을 안내하고 친절하게 응답해주세요.

고객 문의: {query}

결제 지원 응답:"""
)
billing_chain = billing_prompt | llm | parser

# 일반 문의 체인
general_prompt = ChatPromptTemplate.from_template(
    """당신은 친절한 고객 서비스 담당자입니다. 일반적인 문의에 도움을 주세요.

고객 문의: {query}

일반 응답:"""
)
general_chain = general_prompt | llm | parser

# ============================================================
# 3. 라우팅 로직 — 분류 결과에 따라 체인 선택
# ============================================================
route_map = {
    "technical": technical_chain,
    "billing": billing_chain,
    "general": general_chain,
}


def route_query(inputs: dict) -> str:
    """분류 결과에 따라 적절한 체인으로 라우팅합니다."""
    query = inputs["query"]

    # 1) LLM으로 카테고리 분류
    category = classifier_chain.invoke({"query": query}).strip().lower()
    print(f"  분류 결과: {category}")

    # 2) 해당 카테고리의 전문 체인 실행
    chain = route_map.get(category, general_chain)
    response = chain.invoke({"query": query})

    return f"[{category.upper()}] {response}"


# RunnableLambda로 래핑
routing_chain = RunnableLambda(route_query)

# ============================================================
# 테스트 실행
# ============================================================
test_queries = [
    "프로그램이 자꾸 충돌하는데 어떻게 해야 하나요?",
    "구독을 취소하고 환불받고 싶습니다.",
    "이 서비스에서 어떤 기능을 제공하나요?",
    "API 연동 시 인증 오류가 발생합니다.",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─' * 50}")
    print(f"테스트 {i}: {query}")
    result = routing_chain.invoke({"query": query})
    print(f"응답: {result[:300]}...")

print("\n" + "=" * 60)
print("설명:")
print("1. Routing 패턴은 LLM이 입력을 분류한 뒤, 카테고리별 전문 체인으로 분기합니다.")
print("2. 분류기(classifier)가 먼저 실행되어 입력의 성격을 판단합니다.")
print("3. 각 분기는 독립적인 프롬프트와 처리 로직을 가져 전문화된 응답을 생성합니다.")
print("4. 새 카테고리가 필요하면 전문 체인만 추가하면 되므로 확장이 용이합니다.")
print("\n적합한 사용 사례: 고객 서비스, 멀티 도메인 Q&A, 요청 유형별 처리")
