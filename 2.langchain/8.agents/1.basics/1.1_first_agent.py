"""
create_react_agent — 도구 사용 LLM 을 한 줄로 만드는 함수 (현행 표준).
이 예제: 도구 1개 (수학 계산) 를 가진 가장 단순한 에이전트.

에이전트가 하는 일:
  1) 질문을 받고
  2) 도구가 필요한지 LLM 이 판단
  3) 필요하면 도구 호출 → 결과 → 다시 LLM 호출 → ... 반복 (ReAct 루프)
  4) 도구 없이 답할 수 있게 되면 최종 답변

  ※ 자동 루프는 LangGraph 내부에서 처리. 우리는 도구만 주면 됨.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()


# 1) 도구 정의 — 가장 단순한 수학 계산기
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: '53 * 7 + 2'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"


# 2) LLM + 도구를 묶어 에이전트 생성 (한 줄)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [calculator])


# 3) 실행 — messages 형식으로 입력
result = agent.invoke({
    "messages": [("user", "(53 * 7 + 2) / 5 는 얼마야?")]
})

# 4) 결과 확인 — 전체 대화 흐름이 messages 리스트로 옴
print("=== 전체 메시지 흐름 ===")
for m in result["messages"]:
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  [도구 호출]  {c['name']}({c['args']})")
    if m.content:
        prefix = {"human": "[사용자]", "ai": "[AI]", "tool": "[도구 결과]"}.get(m.type, m.type)
        print(f"  {prefix} {m.content}")

print(f"\n최종 답변: {result['messages'][-1].content}")
