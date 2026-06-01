"""
Flask RAG 웹앱 #4 — 구조화 리팩토링(routes/ + services/) + 점수/출처 표시.

빌드업: #1 → #2 → #3 → #4
  #1 minimal             : PDF 1개 업로드 + 질문
  #2 file_append         : 여러 PDF 누적 + 목록
  #3 file_delete         : + 문서 삭제 (문서 다루기 완성)
  #4 refactor_with_score : (#3 기능 전부) + 구조화 리팩토링 + 점수/출처 표시  ← 여기

#3 와의 차등:
  1) 구조 — 한 파일(app.py)에 몰려 있던 코드를 계층으로 분리.
       routes/    : HTTP 라우팅 (Blueprint)
                      page_bp  → GET /
                      files_bp → GET /files, POST /upload, DELETE /files/<source>
                      qa_bp    → POST /ask
       services/  : 도메인 로직
                      vectorstore.py → 벡터 DB / 문서 (add/list/delete/search)
                      qa_service.py  → 질문→답변 (점수/출처 포함)
       app.py     : Blueprint 등록만 하는 얇은 진입점(앱 팩토리)
  2) 답변 — search_with_score 로 검색해 출처(파일/페이지/유사도%)를 함께 반환.
  3) 화면 — 답변 아래 출처 목록 표시 + 로딩 스피너.

기능(업로드 누적 / 목록 / 삭제)은 #3 와 동일하다.
"""

from flask import Flask

from routes import page_bp, files_bp, qa_bp


def create_app() -> Flask:
    """앱 팩토리 — Blueprint(라우팅)를 등록해 Flask 앱을 조립."""
    app = Flask(__name__)
    app.register_blueprint(page_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(qa_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5002)
