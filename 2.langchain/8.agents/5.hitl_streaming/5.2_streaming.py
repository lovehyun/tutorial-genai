"""
agent.stream() — 에이전트의 동작을 실시간 스트리밍.
이 예제: 두 가지 스트림 모드를 비교 — 단계별(step) vs 토큰별(token).

왜 스트리밍?
  - 챗봇 UX 의 기본 — 답변 다 끝날 때까지 기다리지 않음
  - 디버깅 시 "지금 어느 도구를 부르는지" 실시간 추적
  - 긴 응답을 토큰 단위로 흘려보내며 progressive UI 갱신

두 가지 stream_mode:
  - "values"  : 매 노드 끝날 때마다 전체 상태 스냅샷 (메시지 누적 보임)
  - "updates" : 매 노드의 변화분만 (가벼움, 노드 추적에 좋음)
  - "messages": 토큰 단위 LLM 출력 (챗봇 UX)
"""

from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()


@tool
def calculator(expression: str) -> str:
    """수학 식 계산."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


@tool
def get_current_time() -> str:
    """현재 시각."""
    return datetime.now().strftime("%H:%M:%S")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [calculator, get_current_time])

question = "지금 몇 시야? 그리고 153 * 24 는?"


# ─── (1) stream_mode="updates" — 노드 단위 진행 추적 ────────
print("=" * 60)
print('(1) stream_mode="updates" — 노드 단위 진행 보기')
print("=" * 60)
for chunk in agent.stream({"messages": [("user", question)]}, stream_mode="updates"):
    # chunk = {"agent": {"messages": [...]}}  또는  {"tools": {"messages": [...]}}
    for node, payload in chunk.items():
        last = payload["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            for c in last.tool_calls:
                print(f"  [{node:5s}] 도구 호출: {c['name']}({c['args']})")
        elif last.type == "tool":
            print(f"  [{node:5s}] 도구 결과: {last.content}")
        elif last.content:
            print(f"  [{node:5s}] 응답: {last.content[:80]}")


# ─── (2) stream_mode="messages" — 토큰 단위 (챗봇 UX) ────────
print("\n" + "=" * 60)
print('(2) stream_mode="messages" — 토큰 단위 스트림')
print("=" * 60)
print("[ai] ", end="", flush=True)
for token, metadata in agent.stream(
    {"messages": [("user", question)]},
    stream_mode="messages",
):
    # token 은 AIMessageChunk — 도구 호출 응답이 아닌 최종 텍스트만 잘 출력
    if token.content and metadata.get("langgraph_node") == "agent":
        print(token.content, end="", flush=True)
print()


# 정리:
#   - 단계 디버깅 / 진행 표시:  stream_mode="updates"
#   - 챗봇 UX 의 진짜 스트림:   stream_mode="messages"
#   - 둘 다:                  multi-stream (agent.astream + custom 처리)
