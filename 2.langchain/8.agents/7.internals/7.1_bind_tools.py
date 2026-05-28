"""
bind_tools() — create_react_agent 가 내부적으로 쓰는 저수준 패턴.
이 예제: 도구 호출 → 결과 회수 → 최종 응답 을 직접 손으로 짜본다 (자동 루프 X).

언제 직접 이 패턴을 쓰나?
  - 도구 호출을 한 번만 받고 끝내고 싶을 때 (자동 루프 불필요)
  - create_react_agent 가 안에서 무슨 일을 하는지 이해하고 싶을 때
  - 도구 결과를 후처리 / 검증 / 변형하고 싶을 때

흐름:
  1) llm.bind_tools([t1, t2]) — LLM 에 도구 알리기
  2) llm 응답에 tool_calls 가 담겨 옴
  3) 우리가 직접 도구 실행하고 ToolMessage 로 결과 회신
  4) 다시 llm 호출 → 최종 답변
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


@tool
def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 더한다."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """두 정수 a 와 b 를 곱한다."""
    return a * b


# ─── 1) LLM 에 도구 바인딩 ────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([add, multiply])


# ─── 2) 1차 호출 — LLM 이 어떤 도구 부를지 결정 ──────────────
question = "3 더하기 5 를 계산하고, 그 결과에 7 을 곱해줘."
response = llm_with_tools.invoke([HumanMessage(content=question)])

print("=" * 60)
print(f"[질문] {question}")
print("=" * 60)
print(f"[content] {response.content or '(빈 문자열 — 도구만 호출)'}")
print(f"[tool_calls]:")
for call in response.tool_calls:
    print(f"  - {call['name']}({call['args']})  [id={call['id']}]")


# ─── 3) 도구 실제 실행 — 우리가 직접 디스패치 ──────────────
tool_map = {"add": add, "multiply": multiply}

messages = [HumanMessage(content=question), response]
for call in response.tool_calls:
    result = tool_map[call["name"]].invoke(call["args"])
    print(f"\n[실행] {call['name']}({call['args']}) → {result}")
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


# ─── 4) 2차 호출 — 결과를 LLM 에 돌려주고 최종 답변 받기 ────
final = llm_with_tools.invoke(messages)
print(f"\n[최종] {final.content}")


# ─────────────────────────────────────────────────────────────
# 이게 create_react_agent 가 내부에서 자동으로 돌리는 루프입니다.
# 두 번째 응답에 또 tool_calls 가 있으면 3차 호출... 끝날 때까지 반복.
# 실전에서는 직접 디스패치 대신 create_react_agent 를 쓰면 1~4 단계가 자동.
# ─────────────────────────────────────────────────────────────
