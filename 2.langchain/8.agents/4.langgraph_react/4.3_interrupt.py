"""
Human-in-the-loop with Interrupt — 위험한 도구 호출 전에 사람에게 승인 요청

`interrupt_before=["tools"]` 옵션을 주면 에이전트가 도구 호출 직전에 멈춤.
사람이 검토 후 승인하면 이어서 실행, 거부하면 그 부분 건너뛰기.

→ 결제, 이메일 전송, DB 변경 같은 "되돌릴 수 없는" 작업에 필수.
→ legacy 의 `5.human_in_loop/` 보다 훨씬 깔끔.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def send_payment(recipient: str, amount: int) -> str:
    """수신자에게 지정 금액을 송금한다. (실제 송금 X — 데모용)"""
    return f"✅ {recipient} 에게 {amount}원 송금 완료"

@tool
def get_balance(account: str) -> int:
    """계좌 잔액 조회 (안전한 작업이라 interrupt 안 함)."""
    return {"alice": 1000000, "bob": 500000}.get(account, 0)


# ─── interrupt_before=["tools"] 로 도구 호출 전 정지 ──────
checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(
    llm,
    [send_payment, get_balance],
    checkpointer=checkpointer,
    interrupt_before=["tools"],         # ← 도구 호출 직전 정지
)


config = {"configurable": {"thread_id": "demo"}}

# ─── 1단계: 에이전트 호출 — 도구 호출 직전에서 멈춤 ──────
print("=" * 60)
print("[user] alice 의 잔액에서 bob 에게 100000원 송금해줘.")
print("=" * 60)

result = agent.invoke(
    {"messages": [("user", "alice 의 잔액에서 bob 에게 100000원 송금해줘.")]},
    config=config,
)

# 정지 시점의 마지막 메시지 (도구 호출 직전)
last_msg = result["messages"][-1]
print("\n[정지된 시점 — 다음 도구 호출 예정]:")
for call in last_msg.tool_calls:
    print(f"  → {call['name']}({call['args']})")


# ─── 2단계: 사용자 승인 받기 ─────────────────────────────────
approval = input("\n이 작업을 승인하시겠습니까? (y/n): ").strip().lower()

if approval == "y":
    # 승인 — 입력 없이 invoke 하면 정지된 지점부터 이어 실행
    print("\n[승인 — 이어서 실행]")
    result = agent.invoke(None, config=config)
    print(f"\n[ai] {result['messages'][-1].content}")
else:
    # 거부 — interrupt 상태를 메시지 추가로 종료
    print("\n[거부 — 도구 호출 중단]")
    from langchain_core.messages import AIMessage
    # 도구 호출 메시지 대신 거부 메시지 직접 주입
    agent.update_state(config, {"messages": [AIMessage(content="사용자가 거부하여 송금하지 않았습니다.")]})


# ─────────────────────────────────────────────────────────
# 실전 활용:
#   - 위험한 도구만 interrupt: interrupt_before=["dangerous_tool"] 식으로 노드 명시
#   - 도구 인자 수정: agent.update_state(config, ...) 로 인자 바꿔 재실행
#   - 다른 패턴:
#       `interrupt_after=["tools"]` — 결과 본 뒤 정지 (검증용)
#       `interrupt()` 함수를 도구 내부에서 호출 — 도구 안에서 정지
# ─────────────────────────────────────────────────────────
