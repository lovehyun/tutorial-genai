"""
예제 ③ 원하는 '서버'만 구독 — 고른 server_id 목록만 구독한다.

  PUT /subscriptions 는 넘긴 server_ids 로 구독을 '통째 교체'한다.
  등록되지 않은 id 는 걸러서 알려준다.

실행:
  pip install requests python-dotenv
  python 03_subscribe_selected_servers.py                          # picky-agent ← weather, travel(기본)
  python 03_subscribe_selected_servers.py travel-only travel       # travel 만
  python 03_subscribe_selected_servers.py my-agent weather shopping
                                         └ 컨슈머 id  └── 구독할 서버 id 들 ──┘
"""

import sys

from _market import (ensure_consumer, get_subscriptions, gateway_url,
                     list_servers, set_subscriptions)


def main() -> None:
    args = sys.argv[1:]
    consumer_id = args[0] if args else "picky-agent"
    want = args[1:] or ["weather", "travel"]         # 인자 없으면 기본 예시

    valid = {s["id"] for s in list_servers()}
    pick = [sid for sid in want if sid in valid]
    missing = [sid for sid in want if sid not in valid]
    if missing:
        print(f"⚠ 등록되지 않은 서버(무시): {missing}  · 사용 가능: {sorted(valid)}")
    if not pick:
        print("구독할 유효한 서버가 없습니다. 먼저 서버를 등록하세요(예: 01_register_my_server.py).")
        return

    ensure_consumer(consumer_id)
    set_subscriptions(consumer_id, pick)

    print(f"'{consumer_id}' 구독 설정: {pick}")
    print("구독 확인:", [s["id"] for s in get_subscriptions(consumer_id)])
    print("게이트웨이 주소:", gateway_url(consumer_id))


if __name__ == "__main__":
    main()
