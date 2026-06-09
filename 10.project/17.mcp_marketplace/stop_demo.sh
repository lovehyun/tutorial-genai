#!/usr/bin/env bash
# stop_demo.sh — run_demo.sh 로 띄운 프로세스들을 종료한다.
LOG=/tmp/mcp_market
for name in market travel weather shopping; do
  pid_file="$LOG/$name.pid"
  if [ -f "$pid_file" ]; then
    kill -9 "$(cat "$pid_file")" 2>/dev/null && echo "killed $name"
    rm -f "$pid_file"
  fi
done
