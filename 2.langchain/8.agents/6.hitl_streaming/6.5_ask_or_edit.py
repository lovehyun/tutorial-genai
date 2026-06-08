"""
HITL 메뉴형 — 송금 전에 사람에게 묻고, '금액 수정'까지 고를 수 있게.
이 예제: 도구 호출 직전 정지 후 사람에게  1) 진행  2) 취소  3) 금액 수정  을 물어본다.
        3) 을 고르면 새 금액을 입력받아 그 금액으로 송금하고, 남은 잔고를 보여준다.

6.2 는 y/n 승인, 6.4 는 코드로 인자를 수정했다면,
여기선 '사람이 실행 중에 직접 금액을 입력해 고치는' 대화형 패턴이다.

흐름:
  invoke → tools 직전 정지
  → 메뉴 선택 (1 진행 / 2 취소 / 3 수정)
  → 3 이면 같은 id 의 AIMessage 로 args.amount 만 덮어쓰기 (update_state)
  → invoke(None) 으로 재개 → 송금 실행 → 남은 잔고 출력
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 데모용 계좌 잔고 — 송금하면 차감/증가한다.
BALANCES = {"alice": 1_000_000, "bob": 500_000}


@tool
def send_payment(sender: str, recipient: str, amount: int) -> str:
    """sender 계좌에서 recipient 에게 amount 원을 송금한다. (데모 — 잔고 갱신)"""
    BALANCES[sender] -= amount
    BALANCES[recipient] = BALANCES.get(recipient, 0) + amount
    return f"{sender} → {recipient} {amount}원 송금 완료"


checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [send_payment], checkpointer=checkpointer, interrupt_before=["tools"])
config = {"configurable": {"thread_id": "ask-or-edit"}}


# ─── 1) 도구 호출 직전까지 진행 → 정지 ─────────────────────
question = "alice 잔액에서 bob 에게 100000원 송금해줘."
print(f"[user] {question}")
agent.invoke({"messages": [("user", question)]}, config=config)

ai_msg = agent.get_state(config).values["messages"][-1]
call = ai_msg.tool_calls[0]
args = call["args"]
print(f"\n[에이전트 제안] {args['sender']} → {args['recipient']} {args['amount']}원")


# ─── 2) 사람에게 메뉴로 묻기 ───────────────────────────────
print(f"\n{args['recipient']} 에게 송금을 진행하시겠습니까?")
print("  1. 예 (송금)")
print("  2. 아니오 (취소)")
print("  3. 금액 수정")
choice = input("선택 (1/2/3): ").strip()

if choice == "2":
    print("\n[취소] 송금하지 않았습니다.")

else:
    if choice == "3":                                    # 새 금액 입력받아 인자 덮어쓰기
        new_amount = int(input("새 송금 금액(원)을 입력하세요: ").strip())
        edited = {**call, "args": {**args, "amount": new_amount}}
        
        fixed = AIMessage(content=ai_msg.content, tool_calls=[edited], id=ai_msg.id)  # 같은 id → 덮어쓰기
        agent.update_state(config, {"messages": [fixed]})
        print(f"[수정] 송금액 → {new_amount}원")

    # 1(진행) 또는 3(수정) → 재개해서 실제 송금
    result = agent.invoke(None, config=config)
    final = result["messages"][-1].content
    if not final:                          # 도구 실행 직후 모델이 요약을 생략하면 도구 결과를 표시
        final = result["messages"][-2].content

    print(f"\n[ai] {final}")
    print(f"[잔고] {args['sender']} {BALANCES[args['sender']]}원 / "
          f"{args['recipient']} {BALANCES[args['recipient']]}원")
