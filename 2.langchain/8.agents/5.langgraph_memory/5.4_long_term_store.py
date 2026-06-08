"""
장기 메모리 (Store) — thread(세션) 를 넘어서 유지되는 기억.
이 예제: checkpointer(단기·대화 내) 와 대비되는 cross-thread 영속 메모리를 Store 로 구현.

5.1~5.3 복습:
  - checkpointer(MemorySaver) = thread_id 별 '대화 기록'. 세션이 다르면(=thread 가 다르면) 안 섞임.
  - 즉 "방금 그 대화" 는 기억하지만, 새 세션을 열면 사용자가 누구였는지 모름.

Store 는 무엇이 다른가?
  - namespace(예: user_id) 로 저장 → thread 가 바뀌어도, 심지어 며칠 뒤 새 세션에서도 꺼내 씀.
  - "사용자 프로필 / 선호 / 과거 사실" 같은 장기 지식에 적합.

  ※ 여기선 이해를 위해 모듈 전역 InMemoryStore 를 도구 클로저에서 직접 사용합니다.
     프로덕션에선 create_agent(store=...) 로 주입하고 도구에서 InjectedStore 로 받습니다.
     영속화는 InMemoryStore → PostgresStore 등으로 교체.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv()


# ─── 장기 메모리 저장소 (모든 세션이 공유) ──────────────────
store = InMemoryStore()
NS = ("user_facts", "alice")   # namespace — 보통 (용도, user_id)


@tool
def save_memory(content: str) -> str:
    """사용자에 대해 새로 알게 된 사실을 장기 기억에 저장한다 (세션이 바뀌어도 유지)."""
    import uuid
    store.put(NS, key=str(uuid.uuid4()), value={"text": content})
    return f"장기 기억에 저장됨: {content}"


@tool
def recall_memory(query: str) -> str:
    """사용자에 대해 저장해 둔 장기 기억을 검색한다."""
    items = store.search(NS, query=query)   # 벡터 인덱스 없으면 namespace 전체 반환
    if not items:
        return "저장된 기억이 없습니다."
    return "\n".join(f"- {it.value['text']}" for it in items)


# ─── 에이전트: 단기(checkpointer) + 장기(store 도구) 동시 ───
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(
    llm,
    [save_memory, recall_memory],
    system_prompt=(
        "사용자가 자신에 대한 정보를 주면 save_memory 로 저장하라. "
        "사용자가 자신에 대해 묻거나(이름·취향 등) 과거를 언급하면, 답하기 전에 "
        "반드시 recall_memory 를 먼저 호출해 확인하라. 확인 없이 '기억에 없다'고 답하지 말 것."
    ),
    checkpointer=MemorySaver(),   # 단기(대화 내) 는 그대로 유지
)


def chat(user_input: str, thread_id: str):
    print(f"\n[{thread_id}] Q: {user_input}")
    result = agent.invoke(
        {"messages": [("user", user_input)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    print(f"[{thread_id}] A: {result['messages'][-1].content}")


# ─── 세션 1 — 사실을 저장 ───────────────────────────────────
print("=" * 60)
print("세션 1 (thread 'mon') — 사용자 정보 저장")
print("=" * 60)
chat("내 이름은 앨리스고, 파이썬을 가장 좋아해.", "mon")


# ─── 세션 2 — 완전히 새 thread 인데도 기억함 ────────────────
# checkpointer 만 썼다면 'tue' 는 'mon' 의 대화를 전혀 모름.
# 하지만 장기 기억(store)은 namespace 로 공유되므로 recall 가능.
print("\n" + "=" * 60)
print("세션 2 (thread 'tue') — 새 세션, 그러나 장기 기억은 유지")
print("=" * 60)
chat("내가 누구였는지, 뭘 좋아하는지 기억해?", "tue")


# 정리:
#   - checkpointer = thread 단위 단기 기억 (대화 맥락)        → 5.1~5.3
#   - store        = namespace(user) 단위 장기 기억 (cross-thread)
#   - put(namespace, key, value) / search(namespace, query=) / get(namespace, key)
#   - 영속화: InMemoryStore → PostgresStore, MemorySaver → SqliteSaver/PostgresSaver
