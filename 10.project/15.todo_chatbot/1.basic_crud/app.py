"""
Todo 앱 #1 — 가장 단순한 CRUD (챗봇 없음).
이 예제: Flask + SQLite 로 todo 리스트 CRUD 만. 추후 챗봇이 같은 REST API 를 호출하도록 설계.

REST API:
  GET    /api/todos          : 전체 목록
  POST   /api/todos          : 추가 {text}
  PATCH  /api/todos/<id>     : 토글/수정 {done}
  DELETE /api/todos/<id>     : 삭제

JS 가 위 API 를 호출해 UI 갱신 — 다음 단계에서 챗봇이 같은 API 를 부르면 됨.
"""

import sqlite3
from flask import Flask, render_template, request, jsonify, g

DB_PATH = "todo.db"
app = Flask(__name__)


# ─── DB 헬퍼 ──────────────────────────────────────────────
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
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            text       TEXT    NOT NULL,
            done       INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ─── 라우트 ───────────────────────────────────────────────
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/todos")
def list_todos():
    rows = db().execute("SELECT * FROM todos ORDER BY done, id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/todos")
def add_todo():
    text = (request.get_json() or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    cur = db().execute("INSERT INTO todos (text) VALUES (?)", (text,))
    db().commit()
    row = db().execute("SELECT * FROM todos WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.patch("/api/todos/<int:tid>")
def update_todo(tid):
    data = request.get_json() or {}
    fields, values = [], []
    if "done" in data:
        fields.append("done = ?")
        values.append(1 if data["done"] else 0)
    if "text" in data:
        fields.append("text = ?")
        values.append(data["text"])
    if not fields:
        return jsonify({"error": "no fields to update"}), 400
    values.append(tid)
    db().execute(f"UPDATE todos SET {', '.join(fields)} WHERE id = ?", values)
    db().commit()
    row = db().execute("SELECT * FROM todos WHERE id=?", (tid,)).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@app.delete("/api/todos/<int:tid>")
def delete_todo(tid):
    db().execute("DELETE FROM todos WHERE id = ?", (tid,))
    db().commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
