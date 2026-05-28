"""
Todo 앱 #3 — 챗봇 풀 제어 + 화면 자동 갱신.
이 예제: 챗봇이 자연어로 추가/완료/삭제까지. UI 가 챗봇 응답 후 자동으로 새로고침.

#2 와의 차이:
  - 도구 추가: add_todo / toggle_done / delete_todo
  - 챗봇 응답에 changed=True 가 들어오면 프런트가 todo 목록 자동 새로고침
  - 시스템 프롬프트가 "원하는 도구 부르고 결과 보고" 패턴 명시

대화 예:
  - "회의 자료 준비 추가해줘"          → add_todo
  - "회의 자료 완료 표시해줘"          → toggle_done(done=1)
  - "회의 자료 삭제해줘"               → delete_todo
  - "오늘 할 일 다 보여줘"             → list_todos (#2 와 동일)
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


# ─── DB ───────────────────────────────────────────────────
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


# 챗봇 도구가 부르는 DB 헬퍼 — request context 없이 동작
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ─── 챗봇 도구 4종 (read + create + update + delete) ─────
@tool
def list_todos() -> list[dict]:
    """현재 등록된 모든 todo 를 반환한다. 각 항목은 id, text, done(0/1) 을 가진다."""
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT id, text, done FROM todos ORDER BY done, id DESC")]


@tool
def add_todo(text: str) -> dict:
    """새 todo 를 추가한다. text 는 한 문장의 할 일 설명. 추가된 항목을 반환한다."""
    with _conn() as c:
        cur = c.execute("INSERT INTO todos (text) VALUES (?)", (text,))
        c.commit()
        row = c.execute("SELECT id, text, done FROM todos WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)


@tool
def toggle_done(todo_id: int, done: bool) -> dict:
    """특정 todo 를 완료(done=true) 또는 미완료(done=false) 로 변경한다."""
    with _conn() as c:
        c.execute("UPDATE todos SET done=? WHERE id=?", (1 if done else 0, todo_id))
        c.commit()
        row = c.execute("SELECT id, text, done FROM todos WHERE id=?", (todo_id,)).fetchone()
        if row is None:
            return {"error": f"id={todo_id} 인 todo 가 없음"}
        return dict(row)


@tool
def delete_todo(todo_id: int) -> dict:
    """특정 todo 를 영구 삭제한다."""
    with _conn() as c:
        c.execute("DELETE FROM todos WHERE id=?", (todo_id,))
        c.commit()
    return {"ok": True, "deleted_id": todo_id}


# ─── 에이전트 ─────────────────────────────────────────────
system_prompt = """\
당신은 한국어 todo 어시스턴트입니다. 사용자의 자연어 명령을 적절한 도구로 변환해 처리합니다.

작업 흐름:
1) 사용자 명령이 추가/완료/삭제 같은 변경이면 → 먼저 list_todos 로 현재 상태 파악 (id 확인)
2) 알맞은 도구(add_todo / toggle_done / delete_todo / list_todos) 호출
3) 결과를 한국어로 간결히 보고

원칙:
- "OO 완료" / "OO 끝났어" → toggle_done(done=true)
- "OO 추가" / "OO 해야 해" → add_todo
- "OO 삭제" / "OO 지워줘" → delete_todo
- 모호하면 사용자에게 확인 (예: 어떤 항목인지 id 로 지정해달라)
- 같은 도구 2번 이상 호출 금지
- 결과 보고 1~2 문장으로
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chatbot = create_react_agent(
    llm,
    [list_todos, add_todo, toggle_done, delete_todo],
    prompt=system_prompt,
)


# 화면 자동 갱신용 — 도구 호출 중 변경(쓰기)이 있었는지 판정
WRITE_TOOLS = {"add_todo", "toggle_done", "delete_todo"}


def detect_change(messages) -> bool:
    """대화 중 쓰기 도구가 호출됐으면 True"""
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                if c["name"] in WRITE_TOOLS:
                    return True
    return False


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
    message = (request.get_json() or {}).get("message", "").strip()
    if not message:
        return jsonify({"error": "message required"}), 400

    result = chatbot.invoke(
        {"messages": [("user", message)]},
        config={"recursion_limit": 10},
    )
    return jsonify({
        "answer":  result["messages"][-1].content,
        "changed": detect_change(result["messages"]),    # ← UI 가 이 값 보고 새로고침
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5003)
