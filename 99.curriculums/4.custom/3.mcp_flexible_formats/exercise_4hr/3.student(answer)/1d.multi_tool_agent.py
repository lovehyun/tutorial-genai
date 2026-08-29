"""
1b의 도구 3개(get_word_length, calculate_tip, lookup_user)를 create_agent 에 묶어 실제로 실행한다.

DONE — 2.student(todo) 의 TODO 2개(agent 생성, agent 실행)를 채운 정답.
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

# DONE: create_agent(llm, tools) ← 채움
agent = create_agent(llm, tools)

queries = [
    "'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?",
    "5만원 영수증에 15% 팁 얼마야?",
    "u001 사용자 정보 알려줘.",
]

for q in queries:
    # DONE: agent.invoke({"messages": [("user", q)]}) ← 채움
    result = agent.invoke({"messages": [("user", q)]})
    print(f"\n[질문] {q}")
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 도구 결과: {m.content}")
    print(f"[답변] {result['messages'][-1].content}")
