# MCP 마켓플레이스 단일 이미지.
#  · 기본 CMD = 마켓플레이스(등록서버+게이트웨이) 실행
#  · 데모 서버들은 docker-compose 에서 같은 이미지에 command 만 바꿔 띄운다.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
WORKDIR /app/core
# X-Forwarded-* 는 ProxyFix 가 처리하므로 --root-path 불필요(어떤 prefix든 동작).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
