"""
Human-in-the-loop — 위험한 도구 호출 전에 사람에게 승인 받기.
이 예제: interrupt_before=["tools"] 로 에이전트를 도구 호출 직전에 멈춰 사람이 확인 후 진행.

언제 필수인가:
  - 결제·송금·외부 API 호출 (되돌릴 수 없음)
  - 이메일/메시지 발송
  - DB INSERT/UPDATE/DELETE
  - 시스템 명령 실행

흐름:
  agent.invoke()  → 도구 호출 직전 정지 (interrupt)
  사용자 검토 / 인자 수정 / 승인
  agent.invoke(None, config) → 정지 지점부터 재개
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent   # (구) langgraph.prebuilt.create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def send_payment(recipient: str, amount: int) -> str:
    """수신자에게 지정 금액을 송금한다. (데모 — 실제 송금 X)"""
    return f"✅ {recipient} 에게 {amount}원 송금 완료"


@tool
def get_balance(account: str) -> int:
    """계좌 잔액 조회 (안전한 작업)."""
    return {"alice": 1000000, "bob": 500000}.get(account, 0)


# ─── interrupt_before=["tools"] 로 도구 호출 전 정지 ──────
checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(
    llm,
    [send_payment, get_balance],
    checkpointer=checkpointer,
    interrupt_before=["tools"],     # ← 도구 호출 직전 정지
)

config = {"configurable": {"thread_id": "demo"}}


# ─── 1단계: 에이전트 호출 — 도구 호출 직전에 정지 ──────
question = "alice 의 잔액에서 bob 에게 100000원 송금해줘."
print("=" * 60)
print(f"[user] {question}")
print("=" * 60)

result = agent.invoke({"messages": [("user", question)]}, config=config)

# 정지 시점의 마지막 메시지 — 다음에 부를 도구가 들어 있음
last_msg = result["messages"][-1]
print("\n[정지 시점 — 다음 도구 호출 예정]:")
for call in last_msg.tool_calls:
    print(f"  → {call['name']}({call['args']})")


# ─── 2단계: 사용자 승인 ────────────────────────────────────
approval = input("\n이 작업을 승인하시겠습니까? (y/n): ").strip().lower()

if approval == "y":
    # 입력 없이 invoke → 정지 지점부터 재개
    print("\n[승인 — 이어서 실행]")
    result = agent.invoke(None, config=config)
    print(f"\n[ai] {result['messages'][-1].content}")
else:
    # 거부 — 도구 호출 메시지 대신 거부 메시지를 상태에 주입
    print("\n[거부 — 도구 호출 중단]")
    from langchain_core.messages import AIMessage
    agent.update_state(
        config,
        {"messages": [AIMessage(content="사용자가 거부하여 송금하지 않았습니다.")]},
    )


# 실전 활용:
#   - 위험한 도구만: interrupt_before=["send_payment"] 식으로 노드 명시
#   - 도구 인자 수정 후 재실행: agent.update_state(config, {...}) 으로 tool_calls 의 args 수정
#   - interrupt_after=["tools"]: 결과 본 뒤 정지 (검증 시나리오)
