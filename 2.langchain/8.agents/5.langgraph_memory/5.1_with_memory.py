"""
create_agent + MemorySaver — 멀티턴 대화를 기억하는 에이전트.
이 예제: thread_id 별로 대화/도구 결과가 자동 보존되어, 후속 질문에서 이전 맥락 사용 가능.

핵심 변경점:
  - `checkpointer=MemorySaver()` 한 줄 추가
  - 호출 시 `config={"configurable": {"thread_id": "..."}}` 로 세션 구분

  ※ thread_id 는 6.memory 폴더의 session_id 와 같은 역할 (LangGraph 는 thread_id 라 부름)
  ※ MemorySaver 는 in-memory. 영속화는 SqliteSaver / PostgresSaver 등으로 교체.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def remember_fact(fact: str) -> str:
    """사용자가 알려준 사실을 메모한다 (실제로는 그냥 echo)."""
    return f"메모됨: {fact}"


@tool
def get_weather(city: str) -> str:
    """도시 날씨 조회."""
    return {"서울": "맑음, 22도", "부산": "흐림, 25도"}.get(city, "정보 없음")


# ─── 메모리 체크포인터 ──────────────────────────────────────
checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(
    llm,
    [remember_fact, get_weather],
    checkpointer=checkpointer,   # ← 이 한 줄로 메모리 활성화
)


# ─── thread_id 로 세션 구분 ─────────────────────────────────
def chat(user_input: str, thread_id: str):
    print(f"\n[{thread_id}] Q: {user_input}")
    result = agent.invoke(
        {"messages": [("user", user_input)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    print(f"[{thread_id}] A: {result['messages'][-1].content}")


# ─── 멀티턴 — 같은 thread 안에서 맥락 유지 ──────────────────
print("=" * 60)
print("thread 'alice' — 멀티턴 대화 (맥락 유지)")
print("=" * 60)
chat("내 이름은 앨리스야. 기억해줘.",         "alice")
chat("나는 서울에 살아.",                    "alice")
chat("내가 사는 곳 날씨 어때?",               "alice")  # 도구가 자동으로 "서울" 사용
chat("내 이름이 뭐였지?",                    "alice")  # 첫 메시지 기억


# ─── 다른 thread 는 격리 ────────────────────────────────────
print("\n" + "=" * 60)
print("thread 'bob' — 완전히 새 세션")
print("=" * 60)
chat("내 이름이 뭐였지?",                    "bob")    # 앨리스 정보 모름


# 정리:
#   - MemorySaver()         : 프로세스 메모리 (재시작 시 사라짐)
#   - SqliteSaver(path)     : SQLite 영속화
#   - PostgresSaver(...)    : 프로덕션
