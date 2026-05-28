"""
history.json 보기 — 한글 그대로 디버그 출력

FileChatMessageHistory 가 한글을 \\uXXXX 로 escape 해서 저장하므로,
파일을 텍스트 에디터로 직접 열면 읽기 어렵습니다.
이 스크립트는 JSON 을 파싱해 메시지를 사람이 읽을 수 있게 출력합니다.

사용:
  python 2.4_print_history_util.py                # 기본: history.json
  python 2.4_print_history_util.py 다른파일.json
"""

import json
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "history.json"

with open(PATH, "r", encoding="utf-8") as f:
    messages = json.load(f)

ROLE = {"human": "User", "ai": "AI", "system": "System"}

print(f"=== {PATH} ({len(messages)} 메시지) ===\n")
for i, m in enumerate(messages, 1):
    role = ROLE.get(m.get("type", "?"), m.get("type", "?"))
    content = m.get("data", {}).get("content", "")
    print(f"{i:02d}. [{role}] {content}")
