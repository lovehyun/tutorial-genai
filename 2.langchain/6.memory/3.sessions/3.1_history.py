"""
RunnableWithMessageHistory — 메모리 자동 관리 (단일 세션)

2.storage 의 패턴은 매 호출마다 history.messages 를 직접 넣고
끝나면 add_user_message / add_ai_message 를 일일이 해야 했습니다.

RunnableWithMessageHistory 가 그 작업을 자동으로 해줍니다.
일단 세션 구분 없이 항상 같은 메모리를 쓰는 가장 단순한 형태.
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

memory = InMemoryChatMessageHistory()

# 체인을 메모리로 감싸기 — history 주입/저장이 자동
chain_with_memory = RunnableWithMessageHistory(
    chain,
    lambda _: memory,                  # 항상 같은 메모리 반환 (단일 세션)
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message):
    print(f"\nQ: {message}")
    answer = chain_with_memory.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}},   # 단일 세션이지만 키는 필수
    )
    print(f"A: {answer}")


chat("제 이름은 홍길동입니다.")
chat("저는 등산을 좋아해요.")
chat("제 이름과 취미를 다시 말해줄래요?")
