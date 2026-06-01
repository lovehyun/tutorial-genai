"""
Flask RAG REST API #5 (2단계) — 1단계(app.py) 에 삭제 기능 추가.
이 단계(app2_delete.py): DELETE /files/<source> 추가 + GUI 도 삭제 버튼 있는 버전으로.
해당 문서의 벡터 청크를 삭제합니다(원본 PDF 는 보존 — vectorstore.delete_document 참고).

app.py(1단계) 와의 diff — 딱 세 군데만 늘어남:
  - import 에 delete_document 추가
  - / 가 서빙하는 화면: index.html → index2_delete.html (목록/삭제 UI 포함)
  - DELETE /files/<source> 라우트 추가
  업로드 / 목록 / 질문은 1단계와 100% 동일 → diff 로 '삭제만 추가' 가 한눈에.

실행:
  python app2_delete.py    # → http://localhost:5004  (브라우저로 열면 GUI + 삭제)

테스트 (curl):
  curl -F "file=@sample.pdf" http://localhost:5004/files
  curl http://localhost:5004/files
  curl -X DELETE http://localhost:5004/files/sample.pdf      # 벡터 청크 삭제
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from services.vectorstore import add_pdf, list_documents, delete_document, DATA_DIR   # ← delete_document 추가
from services.qa_service import answer_question

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/")
def index():
    """최소 GUI 서빙 — 1단계와 달리 삭제 UI 가 있는 index2_delete.html 반환"""
    return send_from_directory(STATIC_DIR, "index2_delete.html")


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


# ─── 2단계 신규: 삭제 라우트 ─────────────────────────
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
