"""질문/답변 라우트 — 답변 생성은 services.qa_service 에 위임."""

from flask import Blueprint, request, jsonify

from services.qa_service import answer_question

qa_bp = Blueprint("qa", __name__)


@qa_bp.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    return jsonify(answer_question(question))   # {"answer": ..., "sources": [...]}
