"""
Flask 챗봇 #2 — 사용자별 대화 분리

#1 과 비교 — 무엇이 추가됐는가:
  - `memory` (단일) → `sessions: dict[str, ...]` (사용자별)
  - `get_session_history(session_id)` 함수 추가
  - Flask session 으로 username 보관 + 로그인/로그아웃 라우트
  - chat 호출 시 session_id = username

핵심:
  - 메모리 분리는 RunnableWithMessageHistory 의 callback 한 줄만 바꾸면 끝.

실행:
  pip install flask langchain langchain-openai python-dotenv
  python app.py
  → http://localhost:5002
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()


# ─── LLM 체인 + 사용자별 메모리 ───────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# #1 의 단일 memory 가 사용자별 dict 로 확장됨
sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,                 # ← lambda → 함수로 교체
    input_messages_key="input",
    history_messages_key="history",
)


# ─── Flask 라우트 ─────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key-change-me")


@app.get("/")
def index():
    if "username" not in session:
        return render_template("login.html")
    return render_template("chat.html", username=session["username"])


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    if username:
        session["username"] = username
    return redirect(url_for("index"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.post("/chat")
def chat():
    username = session.get("username")
    if not username:
        return jsonify({"error": "로그인이 필요합니다"}), 401

    message = request.json["message"]
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": username}},   # ← session_id = username
    )
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5002)
