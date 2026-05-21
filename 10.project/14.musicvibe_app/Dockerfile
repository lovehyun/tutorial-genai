# ==========================================================================
# VIBE MUSIC SNS - DOCKER PREMIUM PACKAGING (python:3.12-slim)
# ==========================================================================

# 1. Base Image - 경량성과 보안을 고려한 Python 3.12 Slim 배포판 적용
FROM python:3.12-slim

# 2. 파이썬 런타임 최적화 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 3. 비특권(Non-root) 실행 환경을 위한 전용 시스템 계정 생성 (보안 최우선 적용)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# 4. 종속성 설치 캐싱 효율을 위해 requirements.txt만 먼저 복사
COPY requirements.txt .

# 5. 종속성 설치 (--no-cache-dir 옵션으로 불필요한 캐시 누적 배제 및 크기 경량화)
RUN pip install --no-cache-dir -r requirements.txt

# 6. 소스코드 전체 복사 (.dockerignore 규칙에 따라 안전한 파일만 전달됨)
COPY . .

# 7. SQLite DB가 위치할 인스턴스 경로 권한 설정
#    컨테이너 재시작 시 데이터 보존이 필요할 경우 이 경로를 외부 볼륨(-v) 매핑하여 사용 가능
RUN mkdir -p instance && chown -R appuser:appgroup /app

# 8. 컨테이너 보안을 위해 비특권 실행 유저로 변경
USER appuser

# 9. 서비스 포트 노출
EXPOSE 5000

# 10. 이미지 내부 크기를 줄이기 위해 curl 대신 파이썬 내장 라이브러리를 활용한 초경량 헬스체크 구현
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# 11. Flask 어플리케이션 실행
CMD ["python", "app.py"]
