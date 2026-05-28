"""
대화 자동 요약 + 멀티세션

4.2 와 동일 패턴이지만 session_id 별로 메모리/요약을 분리합니다.
사용자 A 의 요약이 사용자 B 에게 흘러가면 안 되므로 격리는 필수.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage

load_dotenv()
llm        = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 친절한 어시스턴트입니다. "
     "history 에 '(요약)' 시스템 메시지가 있다면 그 사실을 신뢰해 답하세요."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

chatbot = RunnableWithMessageHistory(
    chain, get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

summary_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "다음 대화의 핵심 사실(이름, 나이, 취미 등) 을 잃지 않게 간결히 요약하세요."),
        ("human", "{dialogue}"),
    ])
    | summarizer | StrOutputParser()
)

MAX_MSGS = 6


def summarize_session(session_id: str):
    """해당 세션만 요약 + 최근 1 턴 보존"""
    mem = sessions[session_id]
    dialogue = "\n".join(f"{m.type.upper()}: {m.content}" for m in mem.messages)
    summary = summary_chain.invoke({"dialogue": dialogue})

    tail = mem.messages[-2:]
    mem.clear()
    mem.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        mem.add_message(m)
    return summary


def chat(message, session_id):
    print(f"\n[{session_id}] Q: {message}")
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"[{session_id}] A: {answer}")

    if len(sessions[session_id].messages) > MAX_MSGS:
        s = summarize_session(session_id)
        print(f"  ↳ [{session_id} 자동 요약] {s}")


# 두 사용자 교차 대화 — 세션별로 요약 격리되는지 확인
chat("제 이름은 김철수, 35살이에요.", "user-A")
chat("제 이름은 박영희, 28살이에요.", "user-B")
chat("저는 등산이 취미예요.",         "user-A")
chat("저는 요가가 취미예요.",          "user-B")
chat("강아지 이름은 뽀삐예요.",        "user-A")    # ← A 요약 트리거 부근
chat("제 이름과 취미가 뭐였죠?",       "user-B")    # ← B 자기 정보만 봄
