"""
Flask RAG REST API #5 (1단계) — REST API + 최소 GUI(정적 HTML).

#5 의 의미:
  1~4 와 같은 기능(업로드/누적/목록/삭제/점수)을, 화면을 템플릿 엔진
  (render_template) 으로 만들지 않고 — 백엔드는 순수 JSON REST 로,
  프론트는 static/ 정적 HTML 한 장으로 분리한 버전.
  → 같은 API 를 curl / 모바일 앱 등 어떤 클라이언트로도 호출 가능.

이 단계(app.py): 업로드(여러 개) / 목록 / 질문.
  ※ 삭제는 2단계(app2_delete.py), 문서 선택 검색은 3단계(app3_select.py).

REST 답게 리소스 중심 경로:
  POST /files   (파일 리소스 생성=업로드, 여러 개 가능)
  GET  /files   (목록)
  POST /ask     (질문)

실행:
  python app.py        # → http://localhost:5004  (브라우저로 열면 GUI)

테스트 (curl, GUI 없이 API 만):
  curl -F "file=@sample.pdf" http://localhost:5004/files
  curl http://localhost:5004/files
  curl -X POST http://localhost:5004/ask -H "Content-Type: application/json" -d "{\"question\":\"질문\"}"
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from services.vectorstore import add_pdf, list_documents, DATA_DIR
from services.qa_service import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    """최소 GUI 서빙 — 템플릿 엔진 없이 정적 HTML 그대로 반환"""
    return send_from_directory(STATIC_DIR, "index.html")


@app.post("/files")
def upload():
    uploaded = request.files.getlist("file")
    if not uploaded:
        return jsonify({"error": "파일이 없습니다"}), 400

    results = []
    for file in uploaded:
        if not file or not file.filename:
            continue
        path = os.path.join(DATA_DIR, file.filename)
        file.save(path)
        results.append(add_pdf(path))

    added   = [r["source"] for r in results if r["added"]]
    skipped = [r["source"] for r in results if not r["added"]]
    parts = []
    if added:
        parts.append(f"추가됨: {', '.join(added)}")
    if skipped:
        parts.append(f"건너뜀(중복): {', '.join(skipped)}")

    return jsonify({
        "message": " / ".join(parts) or "처리할 파일이 없습니다",
        "files": list_documents(),
    }), 201


@app.get("/files")
def get_files():
    return jsonify({"files": list_documents()})


@app.post("/ask")
def ask():
    question = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify(answer_question(question))


if __name__ == "__main__":
    app.run(debug=True, port=5004)
