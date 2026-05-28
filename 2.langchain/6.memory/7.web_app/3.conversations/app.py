"""
Flask 챗봇 #3 — 사용자별 + 여러 대화 (새 대화 / 이전 대화 보기)

#2 와 비교 — 무엇이 추가됐는가:
  - 한 사용자가 여러 conversation 을 가질 수 있음
  - "새 대화" 버튼: 새 conversation_id 생성
  - "이전 대화" 사이드바: 클릭으로 전환
  - 저장소: InMemory → SQLChatMessageHistory (서버 재시작해도 보존)

핵심:
  - session_id = "{username}::{conversation_id}" 합성 키
  - get_session_history 의 시그니처/이름은 그대로, 내부 storage 만 SQL 로 교체

실행:
  pip install flask langchain langchain-community langchain-openai python-dotenv sqlalchemy
  python app.py
  → http://localhost:5003
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine, text

load_dotenv()


# ─── LLM 체인 + SQL 영속 메모리 ───────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

DB_URL = "sqlite:///web_chat.db"
engine = create_engine(DB_URL)


def get_session_history(session_id: str) -> SQLChatMessageHistory:
    """session_id = '{username}::{conversation_id}' 형식"""
    return SQLChatMessageHistory(session_id=session_id, connection=engine)


chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


def list_user_conversations(username: str) -> list[str]:
    """username 의 모든 conversation_id 목록 (SQL 직접 조회)"""
    prefix = f"{username}::"
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT session_id FROM message_store WHERE session_id LIKE :p"),
            {"p": prefix + "%"},
        ).all()
    return [r[0].split("::", 1)[1] for r in rows]


# ─── Flask 라우트 ─────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key-change-me")


@app.get("/")
def index():
    if "username" not in session:
        return render_template("login.html")

    username = session["username"]

    # 현재 대화가 없으면 새로 생성
    if not session.get("conversation_id"):
        session["conversation_id"] = str(uuid.uuid4())[:8]
    conv_id = session["conversation_id"]

    # 사이드바: 사용자의 모든 대화 + 현재 대화의 히스토리
    all_convs = list_user_conversations(username)
    history = get_session_history(f"{username}::{conv_id}")
    messages = [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in history.messages
    ]

    return render_template(
        "chat.html",
        username=username,
        current_id=conv_id,
        all_convs=all_convs,
        messages=messages,
    )


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    if username:
        session["username"] = username
        session.pop("conversation_id", None)   # 로그인 시 새 대화로 시작
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.post("/new")
def new_conversation():
    """새 대화 시작 — 새 conversation_id 발급"""
    session["conversation_id"] = str(uuid.uuid4())[:8]
    return redirect(url_for("index"))


@app.get("/conversation/<conv_id>")
def switch_conversation(conv_id):
    """이전 대화로 전환"""
    session["conversation_id"] = conv_id
    return redirect(url_for("index"))


@app.post("/chat")
def chat():
    username = session.get("username")
    conv_id  = session.get("conversation_id")
    if not username or not conv_id:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    message = request.json["message"]
    sid = f"{username}::{conv_id}"
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": sid}},
    )
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5003)
