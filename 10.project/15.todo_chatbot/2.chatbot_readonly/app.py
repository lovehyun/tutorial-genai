"""
Todo 앱 #2 — 챗봇 (조회 전용) 추가.
이 예제: #1 위에 자연어로 todo 를 조회·요약하는 챗봇 패널 추가. CRUD 권한은 아직 없음.

#1 과의 차이:
  - 챗봇 도구: list_todos 1개만 (읽기)
  - POST /chat 라우트 추가
  - UI 우측에 챗봇 패널

  ※ 챗봇이 DB 를 직접 수정할 수 없으니 화면 갱신 문제도 없음 (다음 단계 #3 에서 다룸).
"""

import sqlite3
from flask import Flask, render_template, request, jsonify, g
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

DB_PATH = "todo.db"
app = Flask(__name__)


# ─── DB 헬퍼 (#1 과 동일) ─────────────────────────────────
def db():
    if "_db" not in g:
        g._db = sqlite3.connect(DB_PATH)
        g._db.row_factory = sqlite3.Row
    return g._db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("_db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def fetch_all_todos():
    """챗봇 도구가 부르는 헬퍼 — request context 없이도 동작"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM todos ORDER BY done, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── 챗봇 — 읽기 도구 1개만 ────────────────────────────────
@tool
def list_todos() -> list[dict]:
    """현재 등록된 모든 todo 를 반환한다. 각 항목은 id, text, done(0/1), created_at 을 가진다."""
    return fetch_all_todos()


system_prompt = """\
당신은 사용자의 todo 리스트를 살펴봐주는 한국어 비서입니다.
- 사용자의 질문에 답하려면 항상 list_todos 도구를 호출해 현재 상태부터 확인하세요.
- 같은 도구를 2번 이상 호출하지 마세요 (한 번에 다 받아옴).
- "오늘 할 일", "완료한 것", "남은 것" 같은 질문에 답할 때는 done 필드를 보고 분류해서 답하세요.
- 현재 단계의 챗봇은 **조회 전용**입니다. 추가/완료/삭제 요청이 와도 "이번 단계에서는 조회만 가능합니다" 라고 안내하세요.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chatbot = create_react_agent(llm, [list_todos], prompt=system_prompt)


# ─── 라우트 ────────────────────────────────────────────────
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/todos")
def api_list_todos():
    rows = db().execute("SELECT * FROM todos ORDER BY done, id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/todos")
def api_add():
    text = (request.get_json() or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    cur = db().execute("INSERT INTO todos (text) VALUES (?)", (text,))
    db().commit()
    return jsonify(dict(db().execute("SELECT * FROM todos WHERE id=?", (cur.lastrowid,)).fetchone())), 201


@app.patch("/api/todos/<int:tid>")
def api_update(tid):
    data = request.get_json() or {}
    if "done" in data:
        db().execute("UPDATE todos SET done=? WHERE id=?", (1 if data["done"] else 0, tid))
        db().commit()
    return jsonify(dict(db().execute("SELECT * FROM todos WHERE id=?", (tid,)).fetchone()))


@app.delete("/api/todos/<int:tid>")
def api_delete(tid):
    db().execute("DELETE FROM todos WHERE id = ?", (tid,))
    db().commit()
    return jsonify({"ok": True})


@app.post("/chat")
def chat():
    """챗봇과 대화 — 자연어로 todo 조회"""
    message = (request.get_json() or {}).get("message", "").strip()
    if not message:
        return jsonify({"error": "message required"}), 400

    result = chatbot.invoke(
        {"messages": [("user", message)]},
        config={"recursion_limit": 10},
    )
    return jsonify({"answer": result["messages"][-1].content})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5002)
