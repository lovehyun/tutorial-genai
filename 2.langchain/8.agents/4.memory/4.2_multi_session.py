"""
멀티 세션 — thread_id 로 사용자별 기억 격리.
이 예제: 에이전트는 하나인데, thread_id 가 다르면 대화 기억이 서로 안 섞입니다.

핵심:
  - 같은 agent 인스턴스 + 같은 checkpointer 라도
  - config 의 thread_id 가 세션(사용자) 경계 → alice 의 기억이 bob 에게 안 보임
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [], checkpointer=MemorySaver())   # 도구 없이 '기억하는 챗봇'


def ask(thread_id: str, text: str) -> str:
    out = agent.invoke(
        {"messages": [("user", text)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return out["messages"][-1].content


# 각자 자기 이름을 알려줌 (다른 thread_id = 다른 세션)
print("[alice]", ask("alice", "내 이름은 앨리스야. 기억해줘."))
print("[bob]  ", ask("bob",   "내 이름은 밥이야. 기억해줘."))

# 같은 thread 안에서 후속 질문 → 자기 세션 기억만 사용
print("[alice]", ask("alice", "내 이름이 뭐였지?"))   # → 앨리스
print("[bob]  ", ask("bob",   "내 이름이 뭐였지?"))   # → 밥 (alice 와 안 섞임)

# 정리:
#   - thread_id 별로 체크포인터가 메시지를 따로 보관 → 멀티유저 챗봇의 기본
#   - 영속화가 필요하면 MemorySaver → SqliteSaver / PostgresSaver 로 교체
