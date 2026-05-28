"""
Flask 챗봇 #1 — 단일 사용자 + 메모리 유지

지금까지 배운 InMemoryChatMessageHistory + RunnableWithMessageHistory 를
Flask 위에 얹은 가장 단순한 버전.

핵심:
  - 메모리는 단 하나(`memory`). 누가 접속하든 같은 메모리를 공유.
  - 다음 단계(#2)에서 사용자별로 분리합니다.

실행:
  pip install flask langchain langchain-openai python-dotenv
  python app.py
  → http://localhost:5001
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()


# ─── LLM 체인 + 메모리 ────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()

chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,                    # 항상 같은 메모리 → 단일 세션
    input_messages_key="input",
    history_messages_key="history",
)


# ─── Flask 라우트 ─────────────────────────────────────
app = Flask(__name__)


@app.get("/")
def index():
    return render_template("chat.html")


@app.post("/chat")
def chat():
    message = request.json["message"]
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}},
    )
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
