"""
영속 체크포인터 — SqliteSaver 로 대화를 '파일'에 저장 (재시작해도 유지).
이 예제: MemorySaver(프로세스 메모리) → SqliteSaver(디스크) 한 줄 교체. 껐다 켜도 기억.

  ※ MemorySaver 는 프로세스가 죽으면 사라짐 (5.1~5.5).
    SqliteSaver 는 db 파일에 저장 → 재시작/다른 프로세스에서도 thread_id 로 복구.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def remember(fact: str) -> str:
    """사용자가 알려준 사실을 메모한다."""
    return f"메모됨: {fact}"


DB = "agent_memory.db"
config = {"configurable": {"thread_id": "alice"}}


# ─── 1) 첫 실행: 대화를 sqlite 파일에 저장 ──────────────────
print("=" * 60)
print("1) 첫 세션 — sqlite 에 저장")
print("=" * 60)
with SqliteSaver.from_conn_string(DB) as checkpointer:
    agent = create_agent(llm, [remember], checkpointer=checkpointer)
    agent.invoke({"messages": [("user", "내 이름은 앨리스야. 기억해줘.")]}, config=config)
    print("저장 완료 (agent_memory.db)")


# ─── 2) '재시작' 시뮬레이션: 같은 db 파일을 새로 열어 복구 ──
# 위 with 블록이 닫혀 연결이 끊긴 뒤, 완전히 새 saver 로 같은 파일을 연다.
print("\n" + "=" * 60)
print("2) 재시작 — 같은 db 파일에서 대화 복구")
print("=" * 60)
with SqliteSaver.from_conn_string(DB) as checkpointer:
    agent = create_agent(llm, [remember], checkpointer=checkpointer)
    state = agent.get_state(config)
    print(f"복구된 메시지 수: {len(state.values['messages'])}")
    result = agent.invoke({"messages": [("user", "내 이름이 뭐였지?")]}, config=config)
    print(f"답변: {result['messages'][-1].content}")


# 정리:
#   - MemorySaver()  →  SqliteSaver.from_conn_string('file.db')  한 줄 교체로 영속화
#   - 프로세스를 껐다 켜도 thread_id 로 대화 복구
#   - 프로덕션은 PostgresSaver (동시성/확장성)
#   - db 파일(agent_memory.db)은 .gitignore 에 추가 권장
