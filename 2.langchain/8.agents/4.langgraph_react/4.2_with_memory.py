"""
create_react_agent + Memory — 멀티턴 대화를 기억하는 에이전트

LangGraph 의 `checkpointer=MemorySaver()` 를 붙이면 thread_id 별로 대화 상태가 유지된다.
한 thread 안에서 이전 호출의 도구 결과 / 메시지가 모두 보존됨.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


@tool
def remember_fact(fact: str) -> str:
    """사용자가 알려준 사실을 메모한다. (실제로는 그냥 echo)"""
    return f"메모됨: {fact}"

@tool
def get_weather(city: str) -> str:
    """도시 날씨 조회."""
    return {"서울": "맑음, 22도", "부산": "흐림, 25도"}.get(city, "정보 없음")


# ─── MemorySaver 로 thread 별 상태 보존 ──────────────────────
checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [remember_fact, get_weather], checkpointer=checkpointer)


# ─── thread_id 로 세션 구분 ──────────────────────────────────
config = {"configurable": {"thread_id": "user-alice"}}


def chat(user_input: str):
    print(f"\n[user] {user_input}")
    result = agent.invoke({"messages": [("user", user_input)]}, config=config)
    # 마지막 ai 메시지 출력
    final_msg = result["messages"][-1]
    print(f"[ai]   {final_msg.content}")


# ─── 멀티턴 대화 ─────────────────────────────────────────────
print("=" * 60)
print("Thread 'user-alice' 에서 멀티턴 대화")
print("=" * 60)

chat("내 이름은 앨리스야. 기억해줘.")
chat("나는 서울에 살아.")
chat("내가 사는 곳 날씨 어때?")        # ← 앞 대화 기억해서 자동으로 서울 조회
chat("내 이름이 뭐였지?")             # ← 첫 메시지 기억


# ─── 다른 thread_id 는 격리 ──────────────────────────────────
print("\n" + "=" * 60)
print("다른 Thread 'user-bob' — 완전히 새 세션")
print("=" * 60)
config = {"configurable": {"thread_id": "user-bob"}}
chat("내 이름이 뭐였지?")             # ← 앨리스 정보 모름


# ─────────────────────────────────────────────────────────
# 핵심:
#   - MemorySaver() 는 in-memory (프로세스 종료 시 사라짐)
#   - 영속화하려면 SqliteSaver, PostgresSaver 등 사용
#   - thread_id 가 6.memory 의 session_id 와 같은 역할
# ─────────────────────────────────────────────────────────
