# MCP 마켓플레이스 &amp; 게이트웨이

각 팀이 만든 **MCP 서버를 등록**하고, **컨슈머(에이전트)가 원하는 서버를 골라 구독**해서
**게이트웨이를 통해** 사용하는 교육용 플랫폼.

- **등록 서버(Registry)** — 팀이 자기 MCP 서버를 올리면 도구 목록을 자동 수집한다.
- **프록시 게이트웨이(Gateway)** — 소비자는 팀 서버 주소를 몰라도 된다. 게이트웨이 한 곳에만
  붙으면, 구독한 서버들의 도구가 한 묶음으로 들어오고 호출도 게이트웨이가 중계한다.

> **핵심**: 한 팀의 에이전트가 **다른 팀의 MCP 서버**를 구독해서 쓸 수 있다.
> 소비자는 게이트웨이만 보고, 서버 주소·생사 여부는 마켓플레이스가 관리한다.

---

## 구조

```
17.mcp_marketplace/
├── core/                     # 마켓플레이스 본체 (한 프로세스)
│   ├── main.py               #   ASGI 진입점: 게이트웨이(/mcp) + Flask(UI/API) + 헬스 폴링
│   ├── app.py                #   등록서버 REST API + 페이지 라우트 + 통계/로그 API (Flask)
│   ├── gateway.py            #   MCP 프록시 게이트웨이 (저수준 mcp.server.Server) + 호출 기록
│   ├── db.py                 #   SQLite 데이터 레이어 (servers/consumers/subscriptions/tools/calls)
│   ├── mcp_client.py         #   업스트림 서버 probe / call (mcp 클라이언트)
│   ├── security.py           #   공유 Bearer 토큰 + SSRF 방어
│   ├── chat.py               #   채팅 컨슈머 엔진 (OpenAI/Claude tool-calling → 게이트웨이로 실행)
│   └── templates/
│       ├── _base.html        #   공통 레이아웃(네비/스타일) — 모든 페이지가 상속
│       ├── dashboard.html    #   대시보드 (/)        — 상태 분포 + 프록시 통계 시각화
│       ├── browse.html       #   MCP 서버 (/browse) — 검색/필터/등록 + 도구 상세
│       ├── consumers.html    #   컨슈머 (/consumers) — 컨슈머 생성·삭제 + 구독 관리
│       ├── playground.html   #   도구 테스트 (/playground) — raw tool_call + list_tools
│       ├── chat.html         #   채팅 컨슈머 (/chat) — 도구 on/off + LLM 채팅
│       ├── logs.html         #   요청 로그 (/logs)   — IP·입출력, 행 클릭 확장
│       └── guide.html        #   멘티용 SDK 가이드 (/guide)
├── demo/                     # 테스트용 데모 서버 (부팅 시 'demo' 네임스페이스로 셀프 등록)
│   ├── travel_server.py      #   1조 — 여행 (8001)
│   ├── shopping_server.py    #   2조 — 쇼핑 (8003)
│   ├── weather_server.py     #   3조 — 날씨 (8002)
│   └── _selfreg.py           #   부팅 후 /api/servers 로 자기 자신 등록
├── consumer/
│   └── agent.py              # 게이트웨이만 보고 동작하는 LangChain 에이전트 예시
├── requirements.txt
├── run_demo.sh / stop_demo.sh
└── README.md
```

---

## 빠른 시작 (로컬)

```bash
pip install -r requirements.txt

# 마켓플레이스 + 데모 서버 3개를 한 번에 기동
./run_demo.sh
#   → http://localhost:8000/        마켓플레이스 UI
#   → http://localhost:8000/guide   멘티 SDK 가이드

# (다른 터미널) 게이트웨이만 보고 동작하는 에이전트
export OPENAI_API_KEY=sk-...
cd consumer && python agent.py travel-agent "도쿄 여행 예약하고 거기 날씨도 알려줘"

./stop_demo.sh   # 종료
```

데모 서버 3개는 부팅하면서 `demo` 네임스페이스로 **스스로 등록**되므로 수동 시드가 필요 없다.

마켓플레이스만 따로 실행하려면:

```bash
cd core && uvicorn main:app --port 8000
```

---

## 엔드포인트

### 게이트웨이 (MCP, streamable-http)

| 형태 | 주소 | 도구 이름 |
|------|------|-----------|
| 통합 | `/mcp/consumers/<컨슈머id>` | `서버id__도구명` (네임스페이스 prefix) |
| 개별 | `/mcp/servers/<namespace>/<서버id>` | 원래 이름 그대로 |

> 개별 주소의 namespace는 **표시용**이고 라우팅은 유일한 `서버id`(마지막 세그먼트)로 한다.
> 그래서 namespace를 생략한 `/mcp/servers/<서버id>` 도 그대로 동작(하위호환).

### 레지스트리 / UI (HTTP)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 대시보드 (상태 분포 + 프록시 통계) |
| GET | `/browse` | MCP 서버 (검색/필터/등록/도구 상세) |
| GET | `/consumers` | 컨슈머 (생성·삭제 + 구독 관리) |
| GET | `/playground` | 도구 테스트 (raw tool_call) |
| GET | `/chat` | 채팅 컨슈머 (LLM이 도구 사용) |
| GET | `/logs` | 요청 로그 (페이지네이션) |
| GET | `/guide` | 멘티 SDK 가이드 |
| GET/POST | `/api/servers` | 서버 목록 / 등록(+도구 자동 수집) |
| POST | `/api/servers/<id>/refresh` | 도구 재수집 |
| POST | `/api/servers/<id>/call` | 도구 호출(게이트웨이 프록시 경유) — Playground가 사용 |
| DELETE | `/api/servers/<id>` | 삭제 |
| POST | `/heartbeat` | 서버 생존 신고 (선택) |
| GET/POST/DELETE | `/api/consumers` | 컨슈머 |
| GET/PUT | `/api/consumers/<id>/subscriptions` | 구독 |
| GET | `/api/health` | 상태 요약 |
| GET | `/api/stats` | 대시보드 집계 (서버 상태 + 호출 통계) |
| GET | `/api/calls?page=&size=` | 프록시 호출 로그 (최신순, 페이지네이션) |
| GET | `/api/llm` | 채팅에 쓸 수 있는 LLM provider 목록 + 기본값 |
| POST | `/api/chat` | 채팅 — 선택 도구만 노출해 tool-calling, 게이트웨이로 실행 |

모든 프록시 호출(통합/개별/Playground)은 `calls` 테이블에 기록되어 대시보드·로그에 반영된다.
보관은 **건수 기준**(`CALLS_MAX`, 기본 5000)으로, 초과 시 오래된 기록부터 자동 삭제한다.

---

## 헬스 상태 (서버는 절대 즉시 삭제하지 않음)

마켓플레이스가 주기적으로 폴링하여 `last_seen` 기준으로 상태만 바꾼다.

| 상태 | 의미 |
|------|------|
| `ONLINE` | 최근 응답 — 정상 중계 |
| `UNHEALTHY` | 응답이 잠시 늦음 — 아직 중계 시도 |
| `OFFLINE` | 오래 응답 없음 — 호출 시 즉시 `SERVER_OFFLINE` (타임아웃 대신) |
| `ARCHIVED` | 아주 오래 죽음 — 목록에서 흐리게, 메타는 보존 |

임계값은 환경변수로 조정: `HEALTH_ONLINE_SEC`(90), `HEALTH_OFFLINE_SEC`(300),
`HEALTH_ARCHIVE_SEC`(86400), `HEALTH_POLL_SEC`(60), `PROBE_TIMEOUT`(5), `CALLS_MAX`(5000).

---

## 채팅 컨슈머 (`/chat`) — LLM이 도구를 쓰는 실동작 예제

좌측에서 컨슈머와 **사용할 도구를 on/off** 하고, 우측 챗봇으로 대화한다. LLM이 도구를 호출하면
**게이트웨이 프록시로 실행**되므로 그 호출이 요청 로그·대시보드 통계에도 그대로 잡힌다(어떤 도구를
어떤 인자로 불렀는지 대화에 표시).

- **OpenAI / Claude 둘 다 지원.** 키가 둘 다 있으면 GUI 드롭다운에서 모델 선택.
  - `OPENAI_API_KEY` (+ `OPENAI_MODEL`, 기본 `gpt-4o-mini`)
  - `ANTHROPIC_API_KEY` (+ `ANTHROPIC_MODEL`, 기본 `claude-haiku-4-5-20251001`)
  - `LLM_PROVIDER` 로 기본 provider 고정 가능(미설정 시 키 있는 쪽).
- 키/SDK가 **실제 설치·설정된 provider만** 선택지에 노출된다(`pip install openai` / `anthropic`).
- 키는 셸 `export` 또는 프로젝트 `.env`(자동 로드) 어느 쪽이든 된다.

## 인증 / 보안 (데모 배포용 최소 보호)

등록(레지스트리)은 MCP 프로토콜이 아니라 **평범한 HTTP REST** 이고, 게이트웨이는 MCP
streamable-http(=HTTP) 이므로, 둘 다 **공유 Bearer 토큰**으로 보호한다.

- **공유 토큰** (`MARKET_TOKEN`): 설정하면 아래 **관리 작업 + 채팅에만** `Authorization: Bearer <토큰>` 을 요구한다.
  - 토큰 필요: 서버 등록/삭제/재수집, 컨슈머 생성/삭제, 구독 변경(PUT), heartbeat, **채팅(`/api/chat`, LLM 비용)**
  - 토큰 불필요(개방): 모든 읽기, **게이트웨이 `/mcp/*`(MCP 표준)**, 도구 테스트 호출(`/api/servers/<id>/call`)
  - bearer 는 MCP 스펙 요구가 아니라 *남용 방지용 우리 선택*이라, 실제 MCP 트래픽은 열어 둔다.
  - 미설정 시 인증 비활성(로컬 개발). UI 우상단 **🔑 토큰**에서 토큰 확인/복사(데모는 자동 첨부).
- **토큰 UI 노출** (`SHOW_TOKEN_IN_UI`): `1` 이면 `/api/token-hint` 가 토큰을 알려줘 UI가 자동으로
  채운다(데모 편의 — 클릭조차 불필요). **단 이때 쓰기는 사실상 공개**(페이지를 여는 누구나 토큰 획득)이므로,
  진짜 보호가 필요하면 끄고(기본 0) 토큰을 화면 밖(슬라이드/슬랙)으로 전달한다. `run_demo.sh` 는 데모용으로 켜둔다.
- **SSRF 방어**: 등록 `endpoint` 의 호스트를 DNS로 풀어 사설/루프백/링크로컬(메타데이터 `169.254.169.254`
  포함)/예약 IP 면 `400 ENDPOINT_REJECTED` 로 거부. 프록시가 등록자 URL에 직접 접속하므로 필수.
  로컬 올인원 데모는 `127.0.0.1` 자가등록 때문에 `ALLOW_PRIVATE_ENDPOINTS=1` 로 예외 허용
  (`run_demo.sh` 가 자동 설정). **클라우드 배포 시엔 이 값을 끄세요(기본 0).**

```bash
# 클라우드 배포 예
export MARKET_TOKEN="$(openssl rand -hex 24)"   # 학생들에게 공유
# ALLOW_PRIVATE_ENDPOINTS 는 설정하지 않음(=0) → 내부망/메타데이터 차단
cd core && uvicorn main:app --host 0.0.0.0 --port 8000 --root-path /mcp-market
```

> 참고: SSRF 검사는 등록 시점의 DNS 기준이라 TOCTOU(이후 DNS 변경) 한계가 있다. 수업 데모엔 충분하며,
> 더 엄격히 하려면 호출 시점 IP 재검증/아웃바운드 방화벽을 둔다.

## Docker 배포 (nginx + 동적 prefix)

`Dockerfile`, `docker-compose.yml`, `deploy/nginx.conf` 가 들어 있다. compose 는
**마켓플레이스 + 데모서버 3개 + nginx(prefix `/mcp-market`)** 를 한 번에 띄운다.

```bash
# (선택) 채팅용 키 — 없으면 채팅만 비활성, 나머지는 정상
export OPENAI_API_KEY=sk-...        # 또는 ANTHROPIC_API_KEY
export MARKET_TOKEN="$(openssl rand -hex 24)"

docker compose up --build
#   · UI(프록시)     : http://localhost:8080/mcp-market/
#   · UI(직접)       : http://localhost:8000/
```

동적 prefix 처리:
- nginx 가 `X-Forwarded-Host/Proto/Prefix` 를 넘기면 Flask `ProxyFix` 가 `script_root` 에 반영 →
  UI/가이드/게이트웨이 주소가 자동으로 prefix 기준이 된다.
- 게이트웨이는 경로의 키워드(`servers`/`consumers`)와 마지막 세그먼트만 보므로 prefix 에 무관.
- **prefix 변경**: `deploy/nginx.conf` 의 `location /mcp-market/` 와 `X-Forwarded-Prefix /mcp-market`
  두 곳만 같은 값으로 바꾸면 된다.

> 운영 주의: compose 데모는 `ALLOW_PRIVATE_ENDPOINTS=1`·`SHOW_TOKEN_IN_UI=1`(데모 편의)로 켜져 있다.
> 실제 보호가 필요하면 둘 다 0 으로 두고 토큰은 화면 밖으로 배포한다.

---

## 에러 코드 (게이트웨이가 도구 결과 텍스트로 반환)

| error | 의미 |
|-------|------|
| `NOT_SUBSCRIBED` | 컨슈머가 그 서버를 구독하지 않음 |
| `SERVER_OFFLINE` | 대상 서버가 OFFLINE/ARCHIVED |
| `UPSTREAM_ERROR` | 서버는 살아있다고 보였으나 호출 실패 |
| `UNKNOWN_SERVER` / `BAD_TOOL_NAME` | 없는 서버 / 잘못된 도구 이름 형식 |
