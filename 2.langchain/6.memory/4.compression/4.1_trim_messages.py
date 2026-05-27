"""
trim_messages — 토큰/메시지 수 기준으로 대화 이력 자르기

요약(summary) 은 LLM 추가 호출이 필요하지만, trim_messages 는 단순히 잘라내기 때문에
훨씬 가볍고 빠르다. **실무에서 가장 흔한 메모리 압축 방법.**

세 가지 방법 비교:
  - trim_messages (이 파일)  : 오래된 메시지 단순 제거 — 빠름/저렴
  - 요약 (4.2~4.4)          : 오래된 메시지를 요약 — 정보 보존 ↑, LLM 추가 호출 비용
  - 윈도우 (0.legacy)        : 최근 N개만 유지 — 단순하지만 토큰 단위 제어 못함
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, trim_messages,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# (1) trim_messages 단독 사용 — 메시지 리스트 자르기
# ============================================================
messages = [
    SystemMessage(content="당신은 친절한 한국어 어시스턴트입니다."),
    HumanMessage(content="내 이름은 홍길동이야."),
    AIMessage(content="안녕하세요 홍길동님!"),
    HumanMessage(content="좋아하는 색은 파랑이야."),
    AIMessage(content="파랑은 좋은 색이네요."),
    HumanMessage(content="취미는 등산이야."),
    AIMessage(content="등산 좋은 취미네요."),
    HumanMessage(content="최근에 설악산 다녀왔어."),
    AIMessage(content="설악산 멋졌겠네요!"),
    HumanMessage(content="내 이름이 뭐였지?"),
]

trimmed = trim_messages(
    messages,
    max_tokens=80,              # 토큰 한도 (이 안에 들어오게 자름)
    token_counter=llm,          # llm 의 실제 토큰 카운터 사용
    strategy="last",            # 'last' = 최근 메시지 우선 보존
    include_system=True,        # system 메시지는 항상 포함
    allow_partial=False,        # 메시지 일부만 잘라내는 거 금지
    start_on="human",           # human 메시지에서 시작하도록
)

print("=" * 60)
print("자르기 전 메시지 (총 %d개):" % len(messages))
print("=" * 60)
for m in messages:
    print(f"  [{m.type:9s}] {m.content}")

print("\n" + "=" * 60)
print("trim_messages 적용 후 (총 %d개):" % len(trimmed))
print("=" * 60)
for m in trimmed:
    print(f"  [{m.type:9s}] {m.content}")


# ============================================================
# (2) LCEL 체인에 trim 단계 끼우기
# ============================================================
# 매 호출마다 history 를 자동으로 trim 한 뒤 prompt 에 전달
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다. 짧게 답하세요."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

def trim_history(inputs):
    """history 자리에 들어갈 메시지들을 토큰 한도 안으로 자르기"""
    inputs["history"] = trim_messages(
        inputs["history"],
        max_tokens=150,
        token_counter=llm,
        strategy="last",
        include_system=True,
        start_on="human",
    )
    return inputs

chain = RunnableLambda(trim_history) | prompt | llm | StrOutputParser()


# ============================================================
# (3) RunnableWithMessageHistory 와 결합 — 자동 메모리 + trim
# ============================================================
store = {}
def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

print("\n" + "=" * 60)
print("다중 턴 대화 — trim 으로 오래된 메시지 자동 제거")
print("=" * 60)

config = {"configurable": {"session_id": "demo"}}
turns = [
    "내 이름은 홍길동이야.",
    "내 취미는 등산이야.",
    "최근에 설악산 다녀왔어.",
    "다음엔 한라산 가려고 해.",
    "지난 주말엔 영화도 봤어.",
    "내 이름이 뭐였지?",   # ← max_tokens 한도에 따라 trim 으로 잘렸을 수 있음
]
for t in turns:
    ans = with_history.invoke({"input": t}, config=config)
    print(f"\n[user] {t}")
    print(f"[ai]   {ans.strip()}")

# 마지막에 store 상태 확인
print("\n" + "-" * 60)
print(f"세션 저장된 메시지 총 {len(store['demo'].messages)}개:")
for m in store["demo"].messages:
    print(f"  [{m.type:9s}] {m.content[:50]}{'...' if len(m.content) > 50 else ''}")
