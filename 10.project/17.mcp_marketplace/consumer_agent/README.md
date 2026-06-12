# consumer_agent — 소비자(컨슈머) 예제 모음

마켓플레이스 **게이트웨이만 보고** 동작하는 소비자 측 예제들입니다.
소비자는 팀 서버 주소를 몰라도 되고, 게이트웨이 한 곳(`/mcp/consumers/<id>`)에만 붙으면
**구독한 서버들의 도구**가 `서버id__도구명` 으로 합쳐져 들어옵니다.

## 준비

```bash
pip install -r ../requirements.txt -r ../requirements-consumer.txt   # 또는 각 파일 상단의 pip 라인
export MARKET_URL=http://localhost:8000     # 마켓플레이스 주소(기본값)
export MARKET_TOKEN=demo-secret-token       # 등록/구독 등 '관리'에 필요(run_demo.sh 기본 토큰)
# LLM 에이전트(agent.py)만 OPENAI_API_KEY 필요
```

> 먼저 마켓플레이스+데모 서버를 띄워두세요: 상위 폴더에서 `./run_demo.sh`

## 예제

| 파일 | 무엇을 보여주나 | 핵심 |
|------|----------------|------|
| [01_register_my_server.py](01_register_my_server.py) | **내 앱(서버) 등록** | 작은 MCP 서버를 띄우고 `POST /api/servers` 로 셀프 등록 |
| [02_subscribe_all.py](02_subscribe_all.py) | **모두 구독** | 등록된 전체 서버를 한 컨슈머가 구독 |
| [03_subscribe_selected_servers.py](03_subscribe_selected_servers.py) | **원하는 서버만 구독** | 고른 `server_ids` 로 구독을 통째 교체 |
| [04_subscribe_selected_tools.py](04_subscribe_selected_tools.py) | **원하는 서버 내 원하는 도구만** | 구독은 서버 단위 → 도구는 클라이언트에서 필터 |
| [agent.py](agent.py) | **LLM 에이전트(전체)** | 구독 도구로 LangChain 에이전트 구성·대화 |
| [_market.py](_market.py) | (공유 헬퍼) | 02~04 가 쓰는 마켓 API 얇은 래퍼 |

각 파일 상단 주석에 실행법이 있습니다. 구독은 **서버 단위**이며, 도구 단위 선택은
게이트웨이가 주는 도구 목록을 클라이언트에서 거르는 방식(④)이라는 점만 기억하면 됩니다.
