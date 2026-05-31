"""
Flask RAG REST API #4 (2단계) — 1단계(app.py) 에 삭제 기능 추가.
이 단계(app2_delete.py): DELETE /files/<filename> 추가 + GUI 도 삭제 버튼 있는 버전으로.
벡터 + 원본 파일을 함께 삭제합니다.

app.py(1단계) 와의 diff — 딱 세 군데만 늘어남:
  - import 에 delete_file 추가
  - / 가 서빙하는 화면: index.html → index2_delete.html (목록/삭제 UI 포함)
  - DELETE /files/<filename> 라우트 추가
  업로드 / 목록 / 질문은 1단계와 100% 동일 → diff 로 '삭제만 추가' 가 한눈에.

실행:
  python app2_delete.py    # → http://localhost:5004  (브라우저로 열면 GUI + 삭제)

테스트 (curl):
  curl -F "file=@sample.pdf" http://localhost:5004/files
  curl http://localhost:5004/files
  curl -X DELETE http://localhost:5004/files/sample.pdf      # 벡터까지 함께 삭제
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from services.vectorstore import add_pdf, list_files, delete_file, DATA_DIR   # ← delete_file 추가
from services.qa_service import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    """최소 GUI 서빙 — 1단계와 달리 삭제 UI 가 있는 index2_delete.html 반환"""
    return send_from_directory(STATIC_DIR, "index2_delete.html")


@app.post("/files")
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "파일이 없습니다"}), 400
    path = os.path.join(DATA_DIR, file.filename)
    file.save(path)
    add_pdf(path)
    return jsonify({"message": f"'{file.filename}' 업로드 완료"}), 201


@app.get("/files")
def get_files():
    return jsonify({"files": list_files()})


@app.post("/ask")
def ask():
    question = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify(answer_question(question))


# ─── 2단계 신규: 삭제 라우트 ─────────────────────────
@app.delete("/files/<path:filename>")
def remove_file(filename):
    try:
        delete_file(filename)
        return jsonify({"message": f"'{filename}' 삭제 완료"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5004)
