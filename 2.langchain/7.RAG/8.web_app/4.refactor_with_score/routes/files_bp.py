"""문서 파일 라우트 — 목록 / 업로드(누적) / 삭제.

라우팅만 담당하고, 실제 동작은 services.vectorstore 의 함수에 위임한다.
"""

import os
from flask import Blueprint, request, jsonify

from services.vectorstore import add_pdf, list_documents, delete_document, DATA_DIR

files_bp = Blueprint("files", __name__)


@files_bp.get("/files")
def files():
    return jsonify({"files": list_documents()})


@files_bp.post("/upload")
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
    })


@files_bp.delete("/files/<path:source>")
def remove_file(source):
    try:
        existed = delete_document(source)
        msg = f"'{source}' 삭제 완료" if existed else f"'{source}' 은(는) 목록에 없었습니다"
        return jsonify({"message": msg, "files": list_documents()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
