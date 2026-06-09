#!/usr/bin/env bash
# run_demo.sh — 로컬에서 마켓플레이스 + 데모 서버 3개를 한 번에 띄운다.
#   PYTHON 환경변수로 인터프리터 지정 가능 (예: PYTHON=python3.12 ./run_demo.sh)
#   종료: ./stop_demo.sh   (또는 Ctrl+C 후 남은 프로세스 정리)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python}"
LOG=/tmp/mcp_market
mkdir -p "$LOG"

# 데모용 공유 토큰 + 사설 endpoint 허용(로컬은 127.0.0.1 로 자가등록하므로).
# 모든 자식 프로세스(마켓·데모서버)가 상속하도록 export.
export MARKET_TOKEN="${MARKET_TOKEN:-demo-secret-token}"
export ALLOW_PRIVATE_ENDPOINTS="${ALLOW_PRIVATE_ENDPOINTS:-1}"
export SHOW_TOKEN_IN_UI="${SHOW_TOKEN_IN_UI:-1}"   # 데모: UI가 토큰을 자동으로 채움
echo "🔑 MARKET_TOKEN=$MARKET_TOKEN  (UI가 자동 첨부·SDK/에이전트는 동일 토큰 사용)"

echo "▶ 마켓플레이스(등록서버+게이트웨이) 起動 → http://localhost:8000"
( cd "$HERE/core" && exec "$PY" -m uvicorn main:app --port 8000 --log-level info ) > "$LOG/market.log" 2>&1 &
echo $! > "$LOG/market.pid"
sleep 4

for s in travel weather shopping; do
  echo "▶ demo/${s}_server.py 起動 (셀프 등록)"
  ( cd "$HERE/demo" && exec "$PY" "${s}_server.py" ) > "$LOG/${s}.log" 2>&1 &
  echo $! > "$LOG/${s}.pid"
done

sleep 5
echo
echo "✅ 기동 완료. 로그: $LOG/*.log"
echo "   마켓플레이스 UI : http://localhost:8000/"
echo "   SDK 가이드      : http://localhost:8000/guide"
echo "   소비자 에이전트 : (별도 터미널) cd consumer && python agent.py travel-agent"
