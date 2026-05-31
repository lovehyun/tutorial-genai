"""
HITL 심화 — 도구 인자를 사람이 '수정'한 뒤 재개.
5.1 은 승인/거부였다면, 여기선 에이전트가 정한 인자를 사람이 고쳐서 실행합니다.
이 예제: 송금액을 에이전트가 100000 으로 잡았는데, 사람이 50000 으로 낮춰 실행.

흐름:
  invoke → tools 직전 정지
  → 마지막 AIMessage 의 tool_calls 확인
  → 같은 id 로 args 만 고친 AIMessage 로 update_state (덮어쓰기)
  → invoke(None) 으로 재개 → '수정된' 인자로 도구 실행
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def send_payment(recipient: str, amount: int) -> str:
    """수신자에게 지정 금액을 송금한다. (데모 — 실제 송금 X)"""
    return f"✅ {recipient} 에게 {amount}원 송금 완료"


checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [send_payment], checkpointer=checkpointer, interrupt_before=["tools"])
config = {"configurable": {"thread_id": "edit-demo"}}


# 1) 도구 호출 직전까지 진행 → 정지
agent.invoke({"messages": [("user", "bob 에게 100000원 송금해줘.")]}, config=config)

ai_msg = agent.get_state(config).values["messages"][-1]
call = ai_msg.tool_calls[0]
print(f"[에이전트 제안] {call['name']}({call['args']})")


# 2) 사람이 인자 수정 — amount 100000 → 50000
edited = {**call, "args": {**call["args"], "amount": 50000}}
fixed = AIMessage(content=ai_msg.content, tool_calls=[edited], id=ai_msg.id)  # 같은 id → 덮어쓰기
agent.update_state(config, {"messages": [fixed]})
print(f"[사람이 수정]   amount → 50000")


# 3) 재개 — 수정된 인자로 실행
result = agent.invoke(None, config=config)
print(f"[최종] {result['messages'][-1].content}")

# 정리:
#   - 승인/거부(5.1) 를 넘어 '인자 교정' 까지 = 가장 강력한 HITL 패턴
#   - 핵심은 update_state 에 '같은 id' AIMessage 를 넣어 기존 tool_calls 를 덮어쓰는 것
#   - 실전: 금액/수신자/쿼리 등 위험 인자를 사람이 검토·교정 후 실행
