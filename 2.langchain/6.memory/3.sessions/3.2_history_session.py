"""
RunnableWithMessageHistory — session_id 별 분리

서비스에 여러 사용자가 동시에 접속한다면 각 사용자의 대화를 분리해야 합니다.
session_id 마다 다른 InMemoryChatMessageHistory 를 반환하도록 콜백을 바꾸면 끝.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# session_id → 메모리 매핑
sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message, session_id):
    print(f"\n[{session_id}] Q: {message}")
    answer = chain_with_memory.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )
    print(f"[{session_id}] A: {answer}")


user_a = "user-A"
user_b = "user-B"

chat("제 이름은 홍길동입니다.", user_a)
chat("제 이름은 김철수입니다.", user_b)
chat("제 이름이 뭐였죠?", user_a)        # ← A 의 history 만 봄 → "홍길동"
chat("제 이름이 뭐였죠?", user_b)        # ← B 의 history 만 봄 → "김철수"
