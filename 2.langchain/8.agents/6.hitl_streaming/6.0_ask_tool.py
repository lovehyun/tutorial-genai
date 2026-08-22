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
    return f"{recipient} 에게 {amount}원 송금 완료"


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [send_payment])


# ─── 1) 도구 호출 직전까지 진행 → 정지 ─────────────────────
question = "bob 에게 100000원 송금해줘."
print(f"[user] {question}")
result = agent.invoke({"messages": [("user", question)]})

call = result["messages"][-1].tool_calls[0]      # 정지 시점: 부를 도구가 들어 있음
print(f"\n[정지 — 실행 예정] {call['name']}({call['args']})")
