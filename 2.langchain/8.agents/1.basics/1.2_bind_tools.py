"""
bind_tools() — LLM 에 도구를 LCEL 방식으로 바인딩

create_agent / create_react_agent 가 내부적으로 쓰는 더 저수준 패턴이다.
체인에 도구를 직접 끼워넣을 때 사용. agent executor 없이 raw 도구 호출만 보고 싶을 때 유용.

흐름:
  1) llm.bind_tools([tool1, tool2]) 로 LLM 에 도구 알리기
  2) LLM 응답에 tool_calls 가 담겨 옴
  3) 우리가 직접 그 도구를 실행하고 결과를 다시 LLM 에 보내거나, 그냥 종료
"""

import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


# 1. 도구 정의 — @tool 데코레이터로 함수를 도구화
@tool
def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 더한다."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """두 정수 a 와 b 를 곱한다."""
    return a * b


# 2. LLM 에 도구 바인딩
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([add, multiply])


# 3. 1차 호출 — LLM 이 도구 호출을 결정
question = "3 더하기 5 를 계산하고, 그 결과에 7 을 곱해줘."
response = llm_with_tools.invoke([HumanMessage(content=question)])

print("=" * 60)
print("[질문]", question)
print("=" * 60)
print("[LLM 응답 content]", response.content or "(빈 문자열 — 도구만 호출함)")
print("[LLM 이 호출하려는 tool_calls]:")
for call in response.tool_calls:
    print(f"  - {call['name']}({call['args']})")


# 4. 도구 실제 실행 — 우리가 직접 디스패치
tool_map = {"add": add, "multiply": multiply}

messages = [HumanMessage(content=question), response]
for call in response.tool_calls:
    result = tool_map[call["name"]].invoke(call["args"])
    print(f"\n[실행] {call['name']}({call['args']}) → {result}")
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


# 5. 2차 호출 — 도구 결과를 LLM 에 돌려주고 최종 답변 받기
final = llm_with_tools.invoke(messages)
print("\n[최종 답변]", final.content)


# ─────────────────────────────────────────────────────────
# 이게 바로 create_react_agent / create_agent 내부 동작입니다.
# 실전에서는 직접 디스패치 대신 LangGraph의 create_react_agent 를 쓰면
# 위 1~5 단계가 자동으로 반복 (도구 호출이 끝날 때까지).
# → 다음: 4.langgraph_react/4.1_basic.py 참고
# ─────────────────────────────────────────────────────────
