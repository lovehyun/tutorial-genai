"""
@tool 데코레이터 — 일반 파이썬 함수를 LLM 도구로 만들기

세 가지 핵심:
  1) 함수에 @tool 데코레이터 붙이기
  2) 함수의 docstring 이 LLM 에게 보일 도구 설명이 됨
  3) 타입 힌트가 인자 스키마가 됨 (LLM 이 어떤 인자 넣을지 결정할 때 봄)

→ 즉 docstring 과 타입 힌트는 "유저가 보는 주석" 이 아니라 "LLM 이 읽는 명세".
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()


# ─── 1) 가장 단순한 @tool ────────────────────────────────────
@tool
def get_word_length(word: str) -> int:
    """단어의 글자 수를 센다."""
    return len(word)


# ─── 2) 여러 인자 + 명확한 docstring ────────────────────────
@tool
def calculate_tip(amount: float, percent: float) -> float:
    """음식점 영수증 금액과 팁 비율(%)을 받아 팁 금액을 계산한다.

    Args:
        amount: 음식 가격 (원)
        percent: 팁 비율 (예: 15.0 = 15%)
    """
    return amount * percent / 100


# ─── 3) 외부 데이터 조회 도구 (가짜 데이터 사용) ─────────────
@tool
def lookup_user(user_id: str) -> dict:
    """사용자 ID 로 사용자 정보를 조회한다. 존재하지 않으면 빈 dict 반환."""
    db = {
        "u001": {"name": "홍길동", "city": "서울", "age": 30},
        "u002": {"name": "김철수", "city": "부산", "age": 28},
    }
    return db.get(user_id, {})


# ─── LLM 에 바인딩 ──────────────────────────────────────────
tools = [get_word_length, calculate_tip, lookup_user]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)


# ─── 도구가 실제로 어떻게 LLM 에게 보이는지 확인 ─────────────
print("=" * 60)
print("LLM 이 받는 도구 명세:")
print("=" * 60)
for t in tools:
    print(f"\n[Tool] {t.name}")
    print(f"  description: {t.description}")
    print(f"  args_schema: {t.args_schema.model_json_schema() if t.args_schema else 'N/A'}")


# ─── 호출 예시 ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("도구 호출 테스트")
print("=" * 60)

queries = [
    "'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?",
    "5만원 영수증에 15% 팁 얼마야?",
    "u001 사용자 정보 알려줘.",
]

for q in queries:
    response = llm_with_tools.invoke(q)
    print(f"\n[질문] {q}")
    for call in response.tool_calls:
        print(f"  → {call['name']}({call['args']})")


# ─────────────────────────────────────────────────────────
# 다음: 2.2_pydantic_args.py — Pydantic 모델로 인자 스키마를 더 강하게 강제
# ─────────────────────────────────────────────────────────
