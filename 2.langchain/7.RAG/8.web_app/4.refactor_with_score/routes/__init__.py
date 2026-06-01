"""routes 패키지 — 라우팅(HTTP 경로)을 도메인별 Blueprint 로 분리.

  page_bp  : 화면(HTML) 서빙
  files_bp : 문서 목록 / 업로드 / 삭제
  qa_bp    : 질문 / 답변

app.py 는 이 Blueprint 들을 등록만 한다(얇은 진입점).
"""

from routes.page_bp import page_bp
from routes.files_bp import files_bp
from routes.qa_bp import qa_bp

__all__ = ["page_bp", "files_bp", "qa_bp"]
