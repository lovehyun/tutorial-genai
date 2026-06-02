"""
저장된 메모리 들여다보기 — get_state / get_state_history.
이 예제: 체크포인터에 thread 별로 '무엇이' 쌓이는지 직접 꺼내봅니다 (메모리 디버깅).

왜?
  - 멀티턴이 잘 안 될 때 "정말 저장은 되고 있나?" 를 눈으로 확인
  - 토큰이 계속 늘면 누적 메시지가 원인 → 여기서 길이 확인
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator], checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "demo"}}

# 두 번 대화 → 메모리에 누적
agent.invoke({"messages": [("user", "내 이름은 앨리스야.")]}, config=config)
agent.invoke({"messages": [("user", "123 * 7 은?")]}, config=config)

# 1) 현재 상태 — 지금까지 쌓인 메시지 전체
state = agent.get_state(config)
messages = state.values["messages"]
print(f"=== thread 'demo' 에 저장된 메시지: {len(messages)} 개 ===")
for m in messages:
    tag = {"human": "사용자", "ai": "AI", "tool": "도구"}.get(m.type, m.type)
    print(f"  [{tag}] {(m.content or '(도구 호출)')[:50]}")

# 2) 체크포인트 히스토리 — 노드 한 스텝마다 스냅샷이 쌓임
checkpoints = list(agent.get_state_history(config))
print(f"\n=== 체크포인트(스냅샷) 수: {len(checkpoints)} ===")

# 정리:
#   - get_state(config)         : 지금 그 thread 의 최신 상태
#   - get_state_history(config) : 되감기/디버깅용 과거 스냅샷들
#   - 메시지가 계속 쌓이므로 긴 대화는 trim/summary 전략 필요
