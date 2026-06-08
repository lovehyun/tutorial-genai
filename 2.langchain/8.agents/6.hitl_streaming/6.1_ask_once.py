"""
HITL 가장 단순한 형태 — 도구 실행 전에 한 번 묻고 진행.
이 예제: 송금 도구 호출 직전에 멈춰 y/n 을 한 번만 묻는다.
        y → 재개해서 실행하고 결과 출력 / n → 중단 메시지 출력하고 종료.

  - interrupt_before=["tools"] 로 도구 호출 직전 정지.
  - 사람이 승인하면 invoke(None, config) 으로 정지 지점부터 재개.
  - 도구를 한 번만 부르는 가장 단순한 흐름 (여러 번 부르는 반복 승인은 6.2 참고).
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


checkpointer = MemorySaver()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [send_payment], checkpointer=checkpointer, interrupt_before=["tools"])
# config["configurable"] — 이 실행에 넘기는 런타임 설정. checkpointer 와 짝으로 동작한다.
#   - thread_id    : 대화 세션 식별자. checkpointer 가 이 id 로 상태를 저장/복원하므로,
#                    invoke(None) 재개도 '같은 thread_id' 라야 정지 지점부터 이어진다.
#                    (다른 값 → 완전히 새 대화, "ask-once" 는 그냥 이 세션 이름표)
#   다른 선택지(키):
#   - checkpoint_id : 특정 과거 체크포인트로 되돌아가 그 시점부터 재개 (time-travel)
#   - checkpoint_ns : 체크포인트 네임스페이스 — 서브그래프/중첩 그래프 상태 구분용
#   - 그 밖에 직접 정의한 값도 넣어 노드에서 꺼내 쓸 수 있다 (configurable fields)
config = {"configurable": {"thread_id": "ask-once"}}


# ─── 1) 도구 호출 직전까지 진행 → 정지 ─────────────────────
question = "bob 에게 100000원 송금해줘."
print(f"[user] {question}")
result = agent.invoke({"messages": [("user", question)]}, config=config)

call = result["messages"][-1].tool_calls[0]      # 정지 시점: 부를 도구가 들어 있음
print(f"\n[정지 — 실행 예정] {call['name']}({call['args']})")


# ─── 2) 한 번 묻기 ─────────────────────────────────────────
approval = input("\n실행할까요? (y/n): ").strip().lower()

if approval == "y":
    result = agent.invoke(None, config=config)   # 재개 → 도구 실행 → 최종 답변
    print(f"\n[ai] {result['messages'][-1].content}")
else:
    print("\n[중단] 사용자가 거부하여 실행하지 않았습니다.")
