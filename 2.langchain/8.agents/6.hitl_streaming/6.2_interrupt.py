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
from langchain.agents import create_agent
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


# ─── 2단계: 도구 호출이 남아 있는 동안 승인 반복 ───────────
#   interrupt_before=["tools"] 는 "도구를 부를 때마다" 멈춘다.
#   이 작업은 get_balance → send_payment 로 2번 멈추므로 루프로 처리한다.
#   마지막 메시지에 tool_calls 가 없으면 = 최종 답변 → 종료.
while result["messages"][-1].tool_calls:
    last_msg = result["messages"][-1]
    print("\n[정지 시점 — 다음 도구 호출 예정]:")
    for call in last_msg.tool_calls:
        print(f"  → {call['name']}({call['args']})")

    approval = input("\n이 작업을 승인하시겠습니까? (y/n): ").strip().lower()
    if approval == "y":
        # 입력 없이 invoke → 정지 지점부터 재개 (이 도구 실행 후 다음 도구 전에 다시 정지)
        print("\n[승인 — 이어서 실행]")
        result = agent.invoke(None, config=config)
    else:
        # 거부 — 도구를 실행하지 않고 중단
        print("\n[거부 — 도구 호출 중단]")
        print("\n[ai] 사용자가 거부하여 작업을 중단했습니다.")
        break
else:
    # tool_calls 없이 빠져나옴 = 최종 답변 도달
    print(f"\n[ai] {result['messages'][-1].content}")


# 실전 활용:
#   - [특정 도구(send_payment) 전에만 멈추려면?]
#       create_agent 는 "모든 도구가 하나의 tools 노드" 라서, interrupt_before 에
#       개별 도구 이름(["send_payment"])을 줄 수 없다. → 여전히 ["tools"] 로 멈춘 뒤,
#       "정지 시점의 도구 이름" 을 보고 분기한다.
#       위 while 루프에서 approval 을 받기(input) 전에 아래 3줄을 끼우면 된다:
#
#           pending = last_msg.tool_calls[0]["name"]
#           if pending != "send_payment":               # get_balance 같은 안전한 도구는
#               result = agent.invoke(None, config=config)  # 묻지 않고 자동 재개
#               continue                                 # → send_payment 일 때만 y/n 질문
#
#   - 도구 인자 수정 후 재실행: agent.update_state(config, {...}) 으로 tool_calls 의 args 수정 (6.4)
#   - interrupt_after=["tools"]: 결과 본 뒤 정지 (검증 시나리오)
