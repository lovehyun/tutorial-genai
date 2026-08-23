# 케이스 2 — 호출자 인증 + 사용자별 스코프 (HTTP + Bearer)

```
analyst ─[Bearer tok-analyst]─┐
admin   ─[Bearer tok-admin]───┤─▶ 하나의 서버 ─▶ 같은 DB
                              └   analyst 는 customers(PII) 못 봄 / admin 은 전체
```

- **하나의 서버가 여러 사용자를 서빙** → 그래서 **HTTP + 사용자별 토큰** 이 필수다.
  (로컬 stdio 는 사용자가 1명뿐이라 '사용자별'이 성립 안 함.)
- **2단계 방어**:
  - **authN(인증)** — 미들웨어가 토큰이 유효한지 검사 → 아니면 `401`.
  - **authZ(인가)** — 각 도구가 그 토큰의 **사용자 스코프**로 접근 테이블을 제한.
- **혼동된 대리인 방지** — 스코프를 **인증된 토큰에만** 바인딩. 요청 본문/LLM 이 말한 값으로 고르지 않는다.

## 실행 (터미널 2개)
```bash
python ../init_db.py           # shop.db 생성
pip install mcp uvicorn

# 터미널 1 — 서버
cd 2.per_user_scope && python server.py     # http://127.0.0.1:8000/mcp

# 터미널 2 — 클라이언트 (analyst / admin / 무토큰 순서로 시연)
cd 2.per_user_scope && python client.py
```

## 기대 결과
| 호출자 | list_tables | products 조회 | customers(PII) 조회 |
|--------|-------------|---------------|----------------------|
| analyst (`tok-analyst`) | products/orders/order_items | ✅ | ❌ `[인가거부]` |
| admin (`tok-admin`) | 전체 | ✅ | ✅ |
| 무토큰/오토큰 | — | — | **401** (접속 거부) |

## 핵심 코드 위치
- 토큰→사용자 매핑: [server.py](server.py) 의 `TOKENS` (실전은 OAuth 검증 + 권한 테이블 조회)
- 요청별 신원 읽기: `_profile(ctx)` — `ctx.request_context.request.headers` 에서 **헤더로** (요청 본문 아님)
- 스코프 강제: `run_query` 가 `referenced_tables(sql) ⊆ 허용` 인지 검사

## HTTPS/TLS로 배포하려면 (데모는 http, 코드는 주석으로 넣어둠)
데모는 로컬이라 평문 `http`지만, 실제 원격 배포는 **HTTPS 필수**(OAuth/Bearer도 HTTPS 위에서). 둘은 공존 불가라 **주석**으로 넣어뒀다:
- **클라이언트**([client.py](client.py)): 정식 인증서면 **URL을 `https://`로만** 바꾸면 끝(httpx가 TLS 자동). 사설 CA/mTLS면 주석의 `tls_factory`(`verify=`/`cert=`)를 `httpx_client_factory`로.
- **서버**([server.py](server.py)): (A) 보통 **앞단 nginx가 TLS 종단** → 파이썬 코드 변경 0. (B) uvicorn 직접 TLS면 `ssl_certfile`/`ssl_keyfile`.
- TLS(채널·서버 인증)와 Bearer(클라 인증)는 **다른 층** → 실전은 `https://` + `Authorization` 헤더 **둘 다**.

## 실전화 포인트
- `TOKENS` 딕셔너리 → **OAuth 2.1 토큰 검증**(서명·만료·스코프) + 사용자/역할 DB.
- 테이블 문자열 검사(교육용)보다 **DB 자체 권한**(GRANT / Row-Level Security / 역할별 뷰·스키마)이 더 견고.
- 전송 계층 인증의 토대는 → [`../../../10.projects/2.remote/2.oauth/`](../../../10.projects/2.remote/2.oauth/)
