"""
Flask RAG 웹앱 #2 — 점수/출처 + 로딩 UI + services/ 모듈 분리.
이 예제: #1 에서 한 파일이었던 로직을 services/ 로 분리하고, 답변에 출처/유사도 표시.

#1 와의 차이:
  - services/vectorstore.py, services/qa_service.py 로 도메인 로직 분리
  - 답변 응답에 sources (파일/페이지/유사도) 포함
  - 프론트에서 로딩 스피너 표시

다음 단계 (#3): 파일 목록 + 삭제 기능
"""

import os
from flask import Flask, request, jsonify, render_template

from services.vectorstore import add_pdf, DATA_DIR
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
    return jsonify(answer_question(question))   # {"answer": ..., "sources": [...]}


if __name__ == "__main__":
    app.run(debug=True, port=5002)
