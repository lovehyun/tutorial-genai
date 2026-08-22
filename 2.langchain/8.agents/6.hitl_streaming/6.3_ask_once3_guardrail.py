"""
HITL + Guardrail 가장 단순한 형태

흐름:
    사용자 요청
        ↓
    LLM이 Tool Call 생성
        ↓
    interrupt_before=["tools"] 에서 정지
        ↓
    [Guardrail]
        ├─ 잘못된 요청 → 즉시 차단
        └─ 정상 요청
              ↓
           [HITL]
           실행할까요? y/n
              ↓
           Tool 실행

예제 정책:
    - 송금액 <= 0원       → Guardrail에서 차단
    - 정상적인 양수 금액   → 사용자에게 y/n 승인 요청
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# ============================================================
# 1. Tool 정의
# ============================================================
@tool
def send_payment(recipient: str, amount: int) -> str:
    """
    수신자에게 지정 금액을 송금한다.
    금액은 반드시 1원 이상이어야 한다.
    """

    # --------------------------------------------------------
    # Tool 내부의 최종 방어선
    # --------------------------------------------------------
    # Guardrail을 우회해서 Tool이 직접 호출되는 경우까지 대비
    if amount <= 0:
        return "송금 실패: 송금 금액은 1원 이상이어야 합니다."

    return f"{recipient} 에게 {amount:,}원 송금 완료"

# ============================================================
# 2. Guardrail
# ============================================================
def check_guardrail(tool_call):
    """
    Tool 호출 내용을 검사한다.

    Returns:
        (True, "")           → 실행 가능
        (False, "이유")      → 실행 차단
    """

    tool_name = tool_call["name"]
    args = tool_call["args"]

    # --------------------------------------------------------
    # send_payment 정책
    # --------------------------------------------------------
    if tool_name == "send_payment":
        amount = args.get("amount")

        # 금액이 없는 경우
        if amount is None:
            return False, "송금 금액이 지정되지 않았습니다."

        # 숫자가 아닌 경우
        if not isinstance(amount, (int, float)):
            return False, "송금 금액이 올바른 숫자가 아닙니다."

        # 0원 또는 음수 송금 차단
        if amount <= 0:
            return False, f"송금 금액은 1원 이상이어야 합니다. 입력값: {amount}원"

    # 모든 검사를 통과
    return True, ""


# ============================================================
# 3. Agent 생성
# ============================================================
checkpointer = MemorySaver()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    llm,
    [send_payment],
    checkpointer=checkpointer,

    # Tool을 실제 실행하기 직전에 멈춤
    interrupt_before=["tools"]
)


# ============================================================
# 4. Thread 설정
# ============================================================
config = {
    "configurable": {"thread_id": "payment-demo"}
}


# ============================================================
# 5. 사용자 요청
# ============================================================
question = "bob 에게 100000원 송금해줘."

print(f"[user] {question}")


# ============================================================
# 6. Agent 실행
#    → Tool 실행 직전에서 interrupt
# ============================================================
result = agent.invoke(
    {"messages": [("user", question)]},
    config=config
)


# ============================================================
# 7. Tool Call 확인
# ============================================================
last_message = result["messages"][-1]

# LLM이 Tool을 호출하지 않은 경우
if not getattr(last_message, "tool_calls", None):
    print(f"\n[ai] {last_message.content}")
    exit()

call = last_message.tool_calls[0]

print("\n[Tool 호출 요청]")
print(f"도구 : {call['name']}")
print(f"인자 : {call['args']}")


# ============================================================
# 8. Guardrail 검사
# ============================================================
allowed, reason = check_guardrail(call)
if not allowed:
    print("\n[GUARDRAIL BLOCK]")
    print(f"실행이 차단되었습니다.")
    print(f"사유: {reason}")
    exit()

print("\n[GUARDRAIL PASS]")
print("정책 검사를 통과했습니다.")


# ============================================================
# 9. HITL
#    Guardrail을 통과한 요청만 사람에게 물어봄
# ============================================================
approval = input("\n실행할까요? (y/n): ").strip().lower()


# ============================================================
# 10. 승인 / 거부
# ============================================================
if approval == "y":
    # 같은 thread_id를 사용하여
    # interrupt된 지점부터 실행 재개
    result = agent.invoke(None, config=config)
    print(f"\n[ai] {result['messages'][-1].content}")
else:
    print("\n[중단] 사용자가 거부하여 실행하지 않았습니다.")
