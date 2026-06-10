# MCP 마켓플레이스 단일 이미지.
#  · 기본 CMD = 마켓플레이스(등록서버+게이트웨이) 실행
#  · 데모 서버들은 docker-compose 에서 같은 이미지에 command 만 바꿔 띄운다.
#
# bullseye(glibc 2.31) 사용 이유: bookworm(slim 기본)의 새 glibc 는 clone3() 시스콜을 쓰는데,
# 구버전 Docker(≤19.03)의 기본 seccomp 프로파일이 clone3 를 막아 "can't start new thread" 가 난다.
# bullseye 는 clone() 를 써서 seccomp=unconfined 없이도 그대로 동작한다.
FROM python:3.12-slim-bullseye

WORKDIR /app
COPY requirements.txt .
# --progress-bar off : 저사양 호스트에서 pip rich 진행바가 스레드를 못 띄우는 문제 회피
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY . .

EXPOSE 8000
WORKDIR /app/core
# X-Forwarded-* 는 ProxyFix 가 처리하므로 --root-path 불필요(어떤 prefix든 동작).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
