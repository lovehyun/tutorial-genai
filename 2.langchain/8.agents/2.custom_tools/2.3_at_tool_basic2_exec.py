"""
적합한 도구가 없을 때 — LLM 이 잘못 호출하지 않고 "없다" 고 답하게 하기.
이 예제: 2.2 와 같은 도구들에, "이름으로 사용자 조회" 처럼 적합한 도구가 없는 질문을 섞고,
        (1) 시스템 프롬프트 가이드 + (2) 빈 tool_calls 처리로 솔직히 답하게 한다.

핵심:
  - bind_tools 기본 tool_choice="auto" → LLM 은 도구를 "안 쓸" 자유가 있다.
  - lookup_user 는 ID 전용인데 "홍길동 정보" 처럼 이름으로 물으면 적합한 도구가 없음.
  - 시스템 프롬프트로 "적합할 때만 써라, 없으면 없다고 해라" 명시 + 코드에서 빈 tool_calls 처리
    → 잘못된 호출 대신 response.content("적합한 도구가 없습니다") 가 나온다.
  - (반대로 bind_tools(tools, tool_choice="any"/"required") 는 무조건 도구 호출 강제 — 주의)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


@tool
def get_word_length(word: str) -> int:
    """단어의 글자 수를 센다."""
    return len(word)


@tool
def calculate_tip(amount: float, percent: float) -> float:
    """음식점 영수증 금액과 팁 비율(%) 을 받아 팁 금액을 계산한다.

    Args:
        amount: 음식 가격 (원)
        percent: 팁 비율 (예: 15.0 = 15%)
    """
    return amount * percent / 100


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


# ─── 적합한 도구가 없을 때 잘못 호출하는 대신 "없다" 고 답하게 하려면 ──
#   (1) 시스템 프롬프트로 가이드  (2) 빈 tool_calls 일 때 모델 답변 출력 (아래 else)
SYSTEM = (
    "도구는 적합할 때만 사용하세요. lookup_user 는 사용자 ID(u001 형식)로만 조회 가능하며 "
    "이름으로는 조회할 수 없습니다. 적합한 도구가 없거나 도구가 요구하는 입력이 없으면 "
    "도구를 호출하지 말고 '적합한 도구가 없습니다'라고 답하세요."
)

queries = [
    "u001 사용자 정보 알려줘.",        # → lookup_user 호출
    "홍길동 사용자 정보 알려줘.",       # → 이름은 조회 불가 → 적합한 도구 없음
    "프랑스 수도는 어디야?",            # → 아예 관련 도구 없음 → 직접 답
]

for q in queries:
    response = llm_with_tools.invoke([SystemMessage(SYSTEM), HumanMessage(q)])
    print(f"\n[질문] {q}")
    if not response.tool_calls:                       # 적합한 도구 없음 → 모델이 직접 답
        print(f"  (도구 없이 답변) {response.content}")
        continue
    for call in response.tool_calls:
        print(f"  → {call['name']}({call['args']})")

        # 실제 호출·결과를 보려면 아래 주석 해제 (@tool 은 .invoke(args) 로 실행)
        # name2tool = {t.name: t for t in tools}
        # result = name2tool[call["name"]].invoke(call["args"])
        # print(f"     = {result}")
