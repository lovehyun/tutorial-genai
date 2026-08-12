"""
1b(=2.2_at_tool_basic)의 도구 3개(get_word_length, calculate_tip, lookup_user)를
2.1_first_agent 의 패턴대로 create_agent 에 묶어 실제로 실행한다.

원본에 정확히 이 조합(도구 3개 + create_agent 실행)은 없다 — 2.1_first_agent(도구 1개, 실행)와
2.3_at_tool_basic2_exec(도구 3개, bind_tools만, 실행부는 주석 처리)를 합친 것.

── llm.bind_tools() (1b) vs create_agent() (1d) — 뭐가 다른가 ──────────

  둘 다 "LLM이 도구를 판단"하는 그 자리는 완전히 같다(내부적으로 create_agent도
  bind_tools를 쓴다). 다른 건 그 판단 "이후"를 누가 처리하느냐다.

    llm.bind_tools(tools)                    create_agent(llm, tools)
    ─────────────────────────────────       ─────────────────────────────────
    llm_with_tools.invoke(q) 한 번 호출       agent.invoke({"messages":[...]}) 한 번 호출
      → LLM이 "이 도구를, 이 인자로"만          → 내부에서 아래를 자동으로 반복(ReAct 루프):
        판단해서 response.tool_calls 로            1) LLM 판단 (bind_tools와 동일한 자리)
        돌려준다                                    2) 판단한 도구를 실제로 실행
      → 도구 함수는 실행되지 않는다                  3) 실행 결과를 메시지에 추가
      → 결과를 LLM에 다시 넣는 것도,                 4) 다시 LLM 호출 (도구 더 필요?)
        직접 코드로 해야 한다                        5) 도구가 더 필요 없으면 최종 답변
    = "판단"까지만 보여준다                     = "판단 + 실행 + 반복 + 최종 답변"까지 전부

  한 줄 요약: create_agent는 bind_tools를 감싸서 "판단 이후"를 자동화한 것이다.
  1b는 "LLM이 뭘 볼지/뭘 고를지"를 날것 그대로 보여주려고 bind_tools를 노출했고,
  1d는 그 판단이 실제로 실행돼서 자연어 답변까지 이어지는 걸 보여주려고 create_agent를 쓴다.

  create_agent가 "1) 판단 → 2) 실행 → 3) 결과 추가 → 4) 재호출 → 5) 최종 답변"을 정확히
  어떻게 자동화하는지 손으로 직접 보고 싶으면 → 1cx.multi_tool_call_manual.py
  (같은 도구 3개를 create_agent 없이 그 5단계를 그대로 코드로 짠 버전, 순서상 1b 다음이라 1cx).
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
agent = create_agent(llm, tools)

queries = [
    "'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?",
    "5만원 영수증에 15% 팁 얼마야?",
    "u001 사용자 정보 알려줘.",
]

for q in queries:
    result = agent.invoke({"messages": [("user", q)]})
    print(f"\n[질문] {q}")
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 도구 결과: {m.content}")
    print(f"[답변] {result['messages'][-1].content}")


# ─── 실행 결과 (2026-08-12, gpt-4o-mini) ──────────────────────
# [질문] 'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수가 몇 개?
#   → 도구 호출: get_word_length({'word': 'pneumonoultramicroscopicsilicovolcanoconiosis'})
#   ← 도구 결과: 45
# [답변] 'pneumonoultramicroscopicsilicovolcanoconiosis' 단어의 글자 수는 45개입니다.
#
# [질문] 5만원 영수증에 15% 팁 얼마야?
#   → 도구 호출: calculate_tip({'amount': 50000, 'percent': 15})
#   ← 도구 결과: 7500.0
# [답변] 5만원 영수증에 15% 팁은 7,500원입니다.
#
# [질문] u001 사용자 정보 알려줘.
#   → 도구 호출: lookup_user({'user_id': 'u001'})
#   ← 도구 결과: {"name": "홍길동", "city": "서울", "age": 30}
# [답변] 사용자 ID "u001"의 정보는 다음과 같습니다: 이름 홍길동, 도시 서울, 나이 30세.
