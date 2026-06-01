"""
Flask RAG REST API #5 (3단계) — 2단계(app2_delete.py) 에 '문서 선택 검색' 추가.
이 단계(app3_select.py): 업로드한 문서 중 선택한 것 안에서만 질문할 수 있게.
  - 아무 것도 안 고르면  → 전체 문서에서 검색 (1·2단계와 동일)
  - 일부만 고르면        → 그 문서들 안에서만 검색 (metadata.source 필터)

app2_delete.py(2단계) 와의 diff — 딱 세 군데만 늘어남:
  - / 가 서빙하는 화면: index2_delete.html → index3_select.html (체크박스 선택 UI)
  - /ask 가 JSON 의 sources(선택된 파일명 리스트) 를 받아 answer_question 에 전달
  - (서비스 계층은 sources 인자만 추가됐을 뿐, 업로드/목록/삭제는 그대로)

실행:
  python app3_select.py    # → http://localhost:5004  (브라우저로 열면 GUI + 문서 선택)

테스트 (curl):
  # 전체 검색
  curl -X POST http://localhost:5004/ask -H "Content-Type: application/json" \
       -d "{\"question\":\"질문\"}"
  # 특정 문서들 안에서만 검색
  curl -X POST http://localhost:5004/ask -H "Content-Type: application/json" \
       -d "{\"question\":\"질문\",\"sources\":[\"문서1.pdf\",\"문서2.pdf\"]}"
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from services.vectorstore import add_pdf, list_documents, delete_document, DATA_DIR
from services.qa_service import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    """최소 GUI 서빙 — 문서 선택(체크박스) UI 가 있는 index3_select.html 반환"""
    return send_from_directory(STATIC_DIR, "index3_select.html")


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
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    # 3단계 신규: 선택된 문서 목록(없으면 None → 전체 검색)
    sources = body.get("sources") or None
    return jsonify(answer_question(question, sources=sources))


@app.delete("/files/<path:source>")
def remove_file(source):
    try:
        existed = delete_document(source)
        msg = f"'{source}' 삭제 완료" if existed else f"'{source}' 은(는) 목록에 없었습니다"
        return jsonify({"message": msg, "files": list_documents()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5004)
