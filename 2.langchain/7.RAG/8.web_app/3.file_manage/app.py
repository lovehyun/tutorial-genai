"""
Flask RAG 웹앱 #3 — 파일 목록 + 삭제 기능 추가.
이 예제: #2 + GET /files (목록), DELETE /files/<name> (삭제).

#2 와의 차이:
  - vectorstore.py 에 list_files / delete_file 추가
  - app.py 에 /files 라우트 두 개 추가
  - 프론트에 파일 목록 UI + 삭제 버튼
"""

import os
from flask import Flask, request, jsonify, render_template

from services.vectorstore import add_pdf, list_files, delete_file, DATA_DIR
from services.qa_service import answer_question

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "파일이 없습니다"}), 400
    path = os.path.join(DATA_DIR, file.filename)
    file.save(path)
    add_pdf(path)
    return jsonify({"message": f"'{file.filename}' 업로드 완료"})


@app.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify(answer_question(question))


# ─── #3 신규: 파일 관리 라우트 ─────────────────────────
@app.get("/files")
def get_files():
    return jsonify({"files": list_files()})


@app.delete("/files/<path:filename>")
def remove_file(filename):
    try:
        delete_file(filename)
        return jsonify({"message": f"'{filename}' 삭제 완료"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5003)
