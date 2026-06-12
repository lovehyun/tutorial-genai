"""
예제 ② 모두 구독 — 한 컨슈머가 '등록된 모든 서버'를 구독한다.

  가장 단순한 경우. 서버가 늘어나면 다시 실행해 최신 전체를 구독하면 된다.

실행:
  pip install requests python-dotenv
  python 02_subscribe_all.py                 # 컨슈머 id = all-agent
  python 02_subscribe_all.py my-agent        # 원하는 컨슈머 id 지정
"""

import sys

from _market import (ensure_consumer, get_subscriptions, gateway_url,
                     list_servers, set_subscriptions)


def main() -> None:
    consumer_id = sys.argv[1] if len(sys.argv) > 1 else "all-agent"

    ensure_consumer(consumer_id)
    all_ids = [s["id"] for s in list_servers()]
    set_subscriptions(consumer_id, all_ids)          # 전체로 통째 교체

    print(f"'{consumer_id}' 가 전체 서버를 구독했습니다: {all_ids or '(등록된 서버 없음)'}")
    print("구독 확인:", [s["id"] for s in get_subscriptions(consumer_id)])
    print("게이트웨이 주소:", gateway_url(consumer_id))


if __name__ == "__main__":
    main()
