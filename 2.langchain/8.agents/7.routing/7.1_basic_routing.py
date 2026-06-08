"""
다중 도구 라우팅 — 어떤 도구를 쓸지 LLM 이 알아서 판단.
이 예제: 계산기 + 위키 + 시간 도구를 등록하고, 질문별로 다른 도구가 호출되는 걸 관찰.

핵심:
  - 별도 라우터 코드 작성 불필요. 도구만 등록하면 LLM 이 tool calling 으로 선택
  - gpt-4o 계열의 tool selection 정확도가 높아서 이 방식이 표준
  - 도구 없이 답할 수 있는 질문은 직접 답함

  ※ Legacy 의 `9.smartagent_router*` 가 직접 if/else 분기 + decide_tool() LLM 호출로
     라우팅을 명시적으로 짰던 것과 대조됨. 200줄+ → 70줄.
"""

from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain.agents import create_agent

load_dotenv()


@tool
def calculator(expression: str) -> str:
    """수학 계산. 입력 예: '15 * 24', '(3+5) * 2'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"


wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko", top_k_results=2, doc_content_chars_max=1500),
    name="wikipedia_ko",
    description="한국어 위키피디아. 사실/배경/인물 정보 조회.",
)


@tool
def get_current_time() -> str:
    """현재 시각을 반환한다 (서버 기준). 시간/날짜 관련 질문에 사용."""
    return datetime.now().isoformat(timespec="seconds")


system_prompt = """\
당신은 사용자 질문에 가장 적합한 도구를 선택해 답하는 한국어 어시스턴트입니다.

도구 선택 기준:
- 계산 / 수식                 → calculator
- 사실 / 인물 / 배경 지식      → wikipedia_ko
- 현재 시각                   → get_current_time
- 위 어디에도 해당 안 되는 질문 → 도구 없이 직접 답변

도구 결과를 그대로 출력하지 말고, 사용자에게 자연스러운 한국어로 풀어 설명하세요.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator, wiki_ko, get_current_time], system_prompt=system_prompt)


questions = [
    "153 곱하기 (3.2 + 4.8) 은?",        # → calculator
    "세종대왕은 누구야?",                # → wikipedia_ko
    "지금 몇 시야?",                      # → get_current_time
    "오늘 기분 어떻게 풀어줄까?",          # → 도구 없이 직접 답
]

for q in questions:
    print("\n" + "=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", q)]})

    used = [
        c["name"] for m in result["messages"]
        if hasattr(m, "tool_calls") and m.tool_calls
        for c in m.tool_calls
    ]
    print(f"[사용 도구] {used or '(없음 — 직접 답변)'}")
    print(f"[답변] {result['messages'][-1].content}")


# 명시적 라우팅이 정말 필요하면? → LangGraph 의 conditional_edges 로 직접 그래프 분기.
# 하지만 거의 모든 경우 LLM 의 tool calling 이 충분.
