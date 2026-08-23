# 3.sql_helpers_auth — DB MCP 서버의 인증 3모델

[`../2.sql_helpers/`](../2.sql_helpers/) 는 **인증이 사실상 필요 없는** 단순형(로컬 sqlite)이었다.
여기서는 **인증이 얽히는 복잡한 상황**을 세 모델로 나눠, 각각 **실행되는 데모**로 보여준다.

핵심 질문은 항상 두 가지다: **① 자격증명은 누가 쥐나 ② 사용자마다 접근이 다른가.**

| | [`1.server_managed/`](1.server_managed/) | [`2.per_user_scope/`](2.per_user_scope/) | [`3.client_supplied/`](3.client_supplied/) |
|---|---|---|---|
| 한 줄 | 서버가 자격증명 다 관리 | 서버 관리 + **사용자별 스코프** | **클라이언트**가 접속정보 제공, 서버는 프록시 |
| 자격증명 소유 | 서버(`.env`/시크릿) | 서버 | **클라이언트(호출자)** |
| 호출자 인증 | ❌ 모두 동일 접근 | ✅ **필수**(누구인지 알아야 스코프) | 대상 DB 가 요구(서버엔 신원 불필요) |
| 전송 | stdio/HTTP | **HTTP + Bearer 필수** | stdio/HTTP |
| 핵심 위험 | 자격증명 보관(최소권한·TLS) | **혼동된 대리인**(A가 B 데이터 못 보게) | 비밀이 **툴 인자로 새면** 유출 |
| 현실 예 | 사내 대시보드 백엔드 | SaaS 멀티테넌트 | 범용 "아무 DB나" 커넥터 |

> 왜 케이스 2만 HTTP 필수? 로컬 stdio 서버는 사용자가 1명(=나)뿐이라 '사용자별'이 성립 안 함.
> 하나의 서버가 여러 사용자를 서빙해야 "이 요청 = 누구"를 알 수 있고, 그건 원격 HTTP + 토큰이라야 가능.

## 공통 준비
```bash
python init_db.py          # shop.db(쇼핑몰) + hr.db(인사) 생성 — 세 케이스 공용
pip install mcp python-dotenv uvicorn
```
- 공유 로직(읽기전용 가드·포맷·조회)은 [`sqlcommon.py`](sqlcommon.py) 한 벌 → 각 `server.py` 가 import.
  세 서버는 **'인증/스코프' 부분만** 다르다(레이어 분리).

## 각 케이스 실행
| 케이스 | 실행 | 보는 것 |
|--------|------|---------|
| 1 | `cd 1.server_managed && python client.py` | 신원 없이 붙어 조인 질의. `connect()` 에 실제 원격 인증(SSL/URL/IAM) how-to |
| 2 | (터미널2개) `python server.py` / `python client.py` | analyst vs admin 스코프 차이 + 무토큰 401 |
| 3 | `cd 3.client_supplied && python client.py` | 같은 서버를 shop.db / hr.db 로 — 대상은 클라가 결정 |

## 관통하는 보안 원칙
- **최소권한**: 조회면 **읽기 전용 DB 계정** + 서버의 SELECT-only 가드(2차 방어).
- **비밀의 위치**: `.env`/시크릿스토어/클라우드 크레덴셜. **툴 인자로 비밀을 흘리지 말 것**(LLM 전사 유출).
- **스코프 바인딩**: 사용자별 권한은 **인증된 신원**에만 묶는다(요청 본문·LLM 발화로 고르지 않기 = 혼동된 대리인 방지).
- **원격은 TLS**, 임의 대상 접속(케이스3)은 **허용 호스트 화이트리스트**.

## 관련
- 단순 무인증 버전 → [`../2.sql_helpers/`](../2.sql_helpers/)
- 전송 계층 인증(OAuth/Bearer)의 토대 → [`../../10.projects/2.remote/2.oauth/`](../../10.projects/2.remote/2.oauth/)
