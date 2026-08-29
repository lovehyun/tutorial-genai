"""
1b의 도구 3개(get_word_length, calculate_tip, lookup_user)를 create_agent 에 묶어 실제로 실행한다.

1b는 llm_with_tools.invoke(q) 로 "LLM이 뭘 부를지 결정"만 보여주고 실행은 안 했다.
여기서는 create_agent 가 그 결정 이후를 이어받아 "도구 실행 → 결과를 LLM에 다시 전달
→ 최종 답변"까지 자동으로 돈다(ReAct 루프).

TODO: llm 과 tools 로 에이전트를 만들고, agent.invoke(...) 로 실행하세요.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

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

# TODO: llm 과 tools 로 에이전트를 만드세요.
#   힌트 — create_agent(llm, tools)
agent = None  # ← 여기를 채우세요

queries = [
    "'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?",
    "5만원 영수증에 15% 팁 얼마야?",
    "u001 사용자 정보 알려줘.",
]

for q in queries:
    # TODO: 에이전트를 실행하세요.
    #   힌트 — agent.invoke({"messages": [("user", q)]})
    result = None  # ← 여기를 채우세요
    print(f"\n[질문] {q}")
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 도구 결과: {m.content}")
    print(f"[답변] {result['messages'][-1].content}")
