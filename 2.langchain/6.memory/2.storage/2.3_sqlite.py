"""
SQLChatMessageHistory — SQLite DB 에 대화 저장

2.1 / 2.2 와 비교: storage 객체 한 줄만 다릅니다.

장점:
  - 동시 접근에 강함 (파일 lock 문제 없음)
  - session_id 컬럼으로 여러 사용자/대화를 한 DB 에 분리해 저장
  - 운영 환경에서도 흔히 쓰이는 패턴
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# 2.1, 2.2 와 비교: storage 한 줄만 다름
DB_URL     = "sqlite:///chat_history.db"
SESSION_ID = "default"   # SQL 은 한 DB 에서 session_id 로 여러 대화 분리 가능

engine  = create_engine(DB_URL)
history = SQLChatMessageHistory(session_id=SESSION_ID, connection=engine)


def chat(message):
    print(f"\nQ: {message}")
    answer = chain.invoke({
        "input":   message,
        "history": history.messages,
    })
    print(f"A: {answer}")
    history.add_user_message(message)
    history.add_ai_message(answer)


chat("제 이름은 홍길동입니다.")
chat("저는 등산을 좋아해요.")
chat("제 이름과 취미를 다시 말해줄래요?")

# 다시 실행하면 chat_history.db 에서 그대로 이어집니다.
# 다른 session_id 로 실행하면 같은 DB 안에서 새 대화로 분리됩니다.

# DB 내용을 직접 보고 싶을 때 (shell):
#   sqlite3 chat_history.db "SELECT session_id, message FROM message_store;"
