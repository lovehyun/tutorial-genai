"""
trim_messages — 토큰 한도 기준으로 대화 이력 자르기

  - 요약 (4.2~) : LLM 추가 호출이 필요 → 비용 발생
  - 윈도우(3.3) : 메시지 개수만 보고 자름 → 토큰 단위 제어 불가
  - trim_messages (이 파일) : 토큰 한도 안으로 단순 자르기 → 가볍고 빠름

**실무에서 가장 흔히 쓰는 메모리 압축 방법.**
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ============================================================
# (1) trim_messages 단독 사용 — 어떻게 자르는지 감 잡기
# ============================================================
print("=" * 60)
print("(1) trim_messages — 메시지 리스트 단독으로 자르기")
print("=" * 60)

messages = [
    SystemMessage(content="당신은 친절한 한국어 어시스턴트입니다."),
    HumanMessage(content="제 이름은 홍길동이에요."),
    AIMessage(content="안녕하세요 홍길동님!"),
    HumanMessage(content="제 취미는 등산이에요."),
    AIMessage(content="멋진 취미네요."),
    HumanMessage(content="최근에 설악산 다녀왔어요."),
    AIMessage(content="설악산 좋죠!"),
    HumanMessage(content="제 이름이 뭐였죠?"),
]

trimmed = trim_messages(
    messages,
    max_tokens=80,
    token_counter=llm,        # llm 의 실제 토큰 카운터 사용
    strategy="last",          # 최근 메시지 우선 보존
    include_system=True,      # SystemMessage 는 항상 포함
    start_on="human",         # human 메시지에서 시작
)

print(f"자르기 전: {len(messages)} 개")
print(f"자른 후:   {len(trimmed)} 개")
for m in trimmed:
    print(f"  [{m.type:6s}] {m.content}")


# ============================================================
# (2) RunnableWithMessageHistory + trim 자동 적용
# ============================================================
print("\n" + "=" * 60)
print("(2) 자동 메모리에 trim 끼우기")
print("=" * 60)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])

def trim_history(inputs):
    """매 호출 직전 history 를 토큰 한도 안으로 자름"""
    inputs["history"] = trim_messages(
        inputs["history"],
        max_tokens=120,
        token_counter=llm,
        strategy="last",
        include_system=True,
        start_on="human",
    )
    return inputs

chain = RunnableLambda(trim_history) | prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()
with_history = RunnableWithMessageHistory(
    chain, lambda _: memory,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "demo"}}
turns = [
    "제 이름은 홍길동이에요.",
    "제 취미는 등산이에요.",
    "최근에 설악산 다녀왔어요.",
    "다음엔 한라산 가려고 해요.",
    "제 이름이 뭐였죠?",       # ← 토큰 한도 안이면 답변, 잘렸으면 모름
]
for t in turns:
    ans = with_history.invoke({"input": t}, config=config)
    print(f"\nQ: {t}")
    print(f"A: {ans}")

print(f"\n저장된 메시지 총 {len(memory.messages)} 개 (메모리는 자르지 않음 — trim 은 LLM 전송 직전에만 적용)")
