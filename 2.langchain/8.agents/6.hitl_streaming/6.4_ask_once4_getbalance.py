"""
Human-in-the-loop + Guardrail + 잔액 조회

흐름:

사용자:
    "alice 의 잔액에서 bob 에게 100000원 송금해줘."

        ↓

    LLM
        ↓
    get_balance(account="alice")
        ↓
    [안전한 조회 도구]
                → HITL 없이 자동 실행
        ↓
    잔액 1,000,000원 확인
        ↓
    LLM
        ↓
    send_payment(account="alice", recipient="bob", amount=100000)
        ↓
    [Guardrail]
            amount <= 0       → 차단
            amount > balance  → 차단
        ↓
    정상
        ↓
    [HITL]
            "송금하시겠습니까? y/n"
        ↓
            y
        ↓
    send_payment 실행
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# ============================================================
# 0. 계좌 데이터
#    실제 환경에서는 DB / 외부 Banking API 등이 됨
# ============================================================
accounts = {
    "alice": 1_000_000,
    "bob": 500_000
}


# ============================================================
# 1. Tool 정의
# ============================================================
@tool
def get_balance(account: str) -> int:
    """
    계좌 잔액을 조회한다.
    안전한 조회 작업이므로 별도 승인이 필요하지 않다.
    """

    return accounts.get(account, 0)


@tool
def send_payment(account: str, recipient: str, amount: int) -> str:
    """
    account 계좌에서 recipient에게 지정 금액을 송금한다.
    """

    # --------------------------------------------------------
    # Tool 내부 최종 방어선
    # --------------------------------------------------------
    # Guardrail 이후 실제 실행 시점에도 다시 검사한다.
    # --------------------------------------------------------

    if amount <= 0:
        return "송금 실패: 송금 금액은 1원 이상이어야 합니다."

    balance = accounts.get(account, 0)
    if amount > balance:
        return (
            f"송금 실패: 잔액이 부족합니다. "
            f"현재 잔액 {balance:,}원 / "
            f"송금 요청 {amount:,}원"
        )

    # 실제 송금 처리
    accounts[account] -= amount
    accounts[recipient] = accounts.get(recipient, 0) + amount

    return (
        f"{account} 계좌에서 "
        f"{recipient} 에게 {amount:,}원 송금 완료\n"
        f"남은 잔액: {accounts[account]:,}원"
    )


# ============================================================
# 2. Guardrail
# ============================================================
def check_guardrail(tool_call):
    """
    send_payment 실행 전에 정책을 검사한다.

    Returns:
        (True, "")       → 실행 가능
        (False, reason)  → 실행 차단
    """

    tool_name = tool_call["name"]
    args = tool_call["args"]

    # send_payment에 대해서만 검사
    if tool_name == "send_payment":
        account = args.get("account")
        amount = args.get("amount")

        # ----------------------------------------------------
        # 계좌 확인
        # ----------------------------------------------------
        if not account:
            return False, "출금 계좌가 지정되지 않았습니다."

        if account not in accounts:
            return False, f"존재하지 않는 계좌입니다: {account}"

        # ----------------------------------------------------
        # 금액 확인
        # ----------------------------------------------------
        if amount is None:
            return False, "송금 금액이 지정되지 않았습니다."

        if not isinstance(amount, (int, float)):
            return False, "송금 금액이 올바른 숫자가 아닙니다."

        if amount <= 0:
            return False, (
                f"송금 금액은 1원 이상이어야 합니다. "
                f"입력값: {amount:,}원"
            )

        # ----------------------------------------------------
        # 현재 잔액 확인
        # ----------------------------------------------------
        current_balance = accounts.get(account, 0)
        if amount > current_balance:
            return False, (
                f"잔액이 부족합니다. "
                f"현재 잔액: {current_balance:,}원 / "
                f"송금 요청: {amount:,}원"
            )

    return True, ""


# ============================================================
# 3. Agent 생성
# ============================================================

checkpointer = MemorySaver()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    llm,
    [get_balance, send_payment],
    checkpointer=checkpointer,

    # 모든 Tool 호출 직전에 정지
    interrupt_before=["tools"]
)

config = {
    "configurable": {
        "thread_id": "payment-demo"
    }
}


# ============================================================
# 4. 사용자 요청
# ============================================================
question = "alice 의 잔액에서 bob 에게 10만원 송금해줘."

print("=" * 60)
print(f"[user] {question}")
print("=" * 60)


# ============================================================
# 5. 첫 Agent 실행
# ============================================================
result = agent.invoke(
    {"messages": [("user", question)]},
    config=config
)


# ============================================================
# 6. Tool Call 처리
# ============================================================
while result["messages"][-1].tool_calls:
    last_msg = result["messages"][-1]
    print("\n[정지 시점 — 다음 도구 호출 예정]")

    for call in last_msg.tool_calls:
        print(f"  → {call['name']}({call['args']})")

    # ========================================================
    # 이번 예제에서는 Tool을 한 번씩 호출한다고 가정
    # ========================================================
    call = last_msg.tool_calls[0]
    tool_name = call["name"]

    # ========================================================
    # 7. get_balance
    #
    # 안전한 READ 작업
    # → 사용자 승인 없이 자동 실행
    # ========================================================
    if tool_name == "get_balance":
        print("\n[안전한 도구 — 자동 승인]")
        print("잔액 조회를 실행합니다.")

        result = agent.invoke(None, config=config)
        continue

    # ========================================================
    # 8. send_payment
    #
    # 위험한 WRITE 작업
    # → 먼저 Guardrail 검사
    # ========================================================
    if tool_name == "send_payment":
        print("\n[Guardrail 검사]")
        allowed, reason = check_guardrail(call)

        # ----------------------------------------------------
        # Guardrail에서 차단
        # ----------------------------------------------------
        if not allowed:
            print("\n[GUARDRAIL BLOCK]")
            print("송금 실행이 차단되었습니다.")
            print(f"사유: {reason}")
            break

        # ----------------------------------------------------
        # Guardrail 통과
        # ----------------------------------------------------
        print("[GUARDRAIL PASS]")
        print("송금 정책 검사를 통과했습니다.")

        account = call["args"]["account"]
        recipient = call["args"]["recipient"]
        amount = call["args"]["amount"]

        current_balance = accounts.get(account, 0)

        print()
        print("송금 정보")
        print(f"  출금 계좌 : {account}")
        print(f"  수신자    : {recipient}")
        print(f"  송금 금액 : {amount:,}원")
        print(f"  현재 잔액 : {current_balance:,}원")
        print(
            f"  송금 후   : "
            f"{current_balance - amount:,}원"
        )


        # ====================================================
        # 9. HITL
        # ====================================================
        approval = input("\n이 송금을 승인하시겠습니까? (y/n): ").strip().lower()
        if approval == "y":
            print("\n[승인 — 송금 실행]")
            result = agent.invoke(None, config=config)
        else:
            print("\n[거부 — 송금 중단]")
            print("[ai] 사용자가 거부하여 송금을 실행하지 않았습니다.")
            break
        continue

    # ========================================================
    # 그 외 Tool이 추가될 경우
    # ========================================================
    print(f"\n[알 수 없는 Tool] {tool_name}")
    break


# ============================================================
# 10. 최종 답변
# ============================================================
else:
    print(f"\n[ai] {result['messages'][-1].content}")


# ============================================================
# 11. 최종 계좌 상태 확인
# ============================================================
print("\n" + "=" * 60)
print("[현재 계좌 상태]")

for account, balance in accounts.items():
    print(f"  {account}: {balance:,}원")

print("=" * 60)
