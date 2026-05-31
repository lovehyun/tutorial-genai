"""
Flask RAG REST API #4 (1단계) — REST API + 최소 GUI(정적 HTML).
3.file_manage 와 같은 기능이지만, 화면을 템플릿 엔진(render_template)으로 만들지 않고
백엔드는 순수 JSON REST 로, 프론트는 static/index.html 한 장으로 분리합니다.
이 단계(app.py): 업로드 / 목록 / 질문.  ※ 삭제는 2단계(app2_delete.py) 에서 추가.

3.file_manage(템플릿) 와의 차이:
  - templates/ + render_template + Jinja 문법 없음
  - 화면은 static/ 의 정적 HTML, 데이터는 전부 fetch → JSON REST 로 주고받음
  - 그래서 같은 API 를 curl / 모바일 앱 등 어떤 클라이언트로도 그대로 호출 가능
  - 업로드 경로도 REST 답게: POST /files (리소스 생성), GET /files (목록)

실행:
  python app.py        # → http://localhost:5004  (브라우저로 열면 GUI)

테스트 (curl, GUI 없이 API 만):
  curl -F "file=@sample.pdf" http://localhost:5004/files
  curl http://localhost:5004/files
  curl -X POST http://localhost:5004/ask -H "Content-Type: application/json" -d "{\"question\":\"질문\"}"
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from services.vectorstore import add_pdf, list_files, DATA_DIR
from services.qa_service import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    """최소 GUI 서빙 — 템플릿 엔진 없이 정적 HTML 그대로 반환"""
    return send_from_directory(STATIC_DIR, "index.html")


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


if __name__ == "__main__":
    app.run(debug=True, port=5004)
