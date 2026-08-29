"""
@tool 데코레이터 — 일반 파이썬 함수를 LLM 도구로 만드는 가장 단순한 방법.

DONE — 2.student(todo) 의 calculate_tip, lookup_user TODO 를 채운 정답.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()


# ─── 1) 가장 단순한 도구 (완성됨 — 아래 DONE 의 패턴 참고용) ──
@tool
def get_word_length(word: str) -> int:
    """단어의 글자 수를 센다."""
    return len(word)


# ─── 2) DONE: get_word_length 와 같은 패턴으로 완성 ────────────
#   요구사항 — 영수증 금액(amount)과 팁 비율(percent, %)을 받아 팁 금액을 반환한다.
#   힌트 1 — get_word_length 처럼 함수 위에 @tool 데코레이터를 붙인다. ← 채움
#   힌트 2 — docstring 은 LLM 이 읽는 "도구 설명"이다. 무슨 도구인지, 인자가 뭔지 적는다. ← 채움
#   힌트 3 — 계산식: amount * percent / 100 ← 채움
@tool
def calculate_tip(amount: float, percent: float) -> float:
    """음식점 영수증 금액과 팁 비율(%) 을 받아 팁 금액을 계산한다.

    Args:
        amount: 음식 가격 (원)
        percent: 팁 비율 (예: 15.0 = 15%)
    """
    return amount * percent / 100


# ─── 3) DONE: get_word_length 와 같은 패턴으로 완성 ────────────
#   요구사항 — user_id 로 db 에서 사용자 정보를 찾아 반환한다. 없으면 빈 dict({}) 반환. ← 채움
#   힌트 — dict 에는 "키가 없을 때 기본값"을 주는 메서드가 있다: db.get(키, 기본값) ← 채움
@tool
def lookup_user(user_id: str) -> dict:
    """사용자 ID 로 사용자 정보를 조회한다. 존재하지 않으면 빈 dict 반환."""
    db = {
        "u001": {"name": "홍길동", "city": "서울", "age": 30},
        "u002": {"name": "김철수", "city": "부산", "age": 28},
    }
    return db.get(user_id, {})


tools = [get_word_length, calculate_tip, lookup_user]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)


print("=" * 60)
print("LLM 이 받는 도구 명세")
print("=" * 60)
for t in tools:
    print(f"\n[Tool] {t.name}")
    print(f"  description: {t.description}")
    print(f"  args_schema: {t.args_schema.model_json_schema() if t.args_schema else 'N/A'}")


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
