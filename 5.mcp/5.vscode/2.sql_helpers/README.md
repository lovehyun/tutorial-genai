# 2.sql_helpers — 내 DB 를 자연어로 질의하는 MCP 서버

DB 를 MCP 서버로 감싸면, 클라이언트(Claude Code / Copilot / Cline …)의 LLM 이
**스키마를 읽고 → SQL 을 스스로 짜서 → 실행**한다. 당신은 *"도시별 총 매출 알려줘"* 처럼
**자연어로만** 물으면 된다.

```
당신: "취소 뺀 도시별 총 매출 알려줘"
 └─ LLM 이 list_tables/describe_table 로 구조 파악
 └─ SELECT c.city, SUM(...) ... JOIN ... GROUP BY  작성
 └─ run_query 호출 → 결과 표 → 자연어로 요약해 답
```

## 지원 DB
접속정보(`.env`)만 바꾸면 **도구 인터페이스는 동일**하다.

| DB | 상태 | 추가 설치 |
|----|------|-----------|
| **SQLite** (로컬 파일) | ✅ 완성본(검증됨) | 없음 (표준 라이브러리) |
| **PostgreSQL** (원격) | 코드 포함 | `pip install "psycopg[binary]"` |
| **MySQL / MariaDB** (원격) | 코드 포함 | `pip install pymysql` |

## 파일
| 파일 | 설명 |
|------|------|
| `init_db.py` | 샘플 SQLite 생성 (쇼핑몰 4테이블 + 데이터) — 조인·집계용 |
| `server.py` | `sql-helper` MCP 서버 (3종 DB, SQLite 완성) |
| `client.py` | 데모/검증용 raw 클라이언트 (조인 질의 + 가드 확인) |
| `.env.example` | 접속정보 템플릿 → `.env` 로 복사 |
| `.vscode/mcp.json` | **VSCode** 설정 — 이 폴더를 Open Folder 하면 자동 인식 |
| `.mcp.json` | **Claude Code** 프로젝트 설정 — 이 폴더에서 `claude` 실행 시 자동 인식 |

## 제공 도구
| 도구 | 설명 |
|------|------|
| `list_tables()` | 테이블 목록 |
| `describe_table(table)` | 컬럼 구조(이름/타입/NULL/PK) |
| `preview_table(table, limit=5)` | 앞부분 몇 행 미리보기 |
| `run_query(sql)` | **읽기 전용** SQL 실행(SELECT/WITH/EXPLAIN). 조인·집계·서브쿼리 OK |
| resource `schema://database` | 전체 스키마 지도(LLM 이 SQL 짤 때 참고) |

## 샘플 스키마 (조인 연습용)
```
customers ─1:N─ orders ─1:N─ order_items ─N:1─ products
```
- `customers`(고객·도시) · `products`(상품·가격·재고) · `orders`(주문·상태) · `order_items`(주문상세)
- 예) "도시별 총 매출" = `customers ⋈ orders ⋈ order_items` 3중 조인 + `GROUP BY`

## 실행 (로컬 SQLite, 완성본)
```bash
pip install mcp python-dotenv
cd 5.mcp/5.vscode/2.sql_helpers
python init_db.py        # sample.db 생성 (필수)
python client.py         # 조인/집계 질의 + 읽기전용 가드 데모
```
> `.env` 없이도 SQLite `./sample.db` 기본값으로 동작한다.

## Claude Code 에 등록해서 자연어로 쓰기
```powershell
# (mcp 깔린 python 필요 — 레포 루트 venv 권장)
claude mcp add sql-helper -- "C:\...\tutorial-genai\.venv\Scripts\python.exe" "C:\...\tutorial-genai\5.mcp\5.vscode\2.sql_helpers\server.py"
claude mcp list          # ✓ Connected 확인
```
등록 후(재시작 뒤) **자연어로** 물으면 된다 — 도구는 `mcp__sql-helper__run_query` 등으로 노출:
- *"sql-helper 로 도시별 총 매출을 취소 주문 빼고 뽑아줘"*
- *"가장 많이 팔린 상품 3개는?"*
- *"부산 고객들이 주문한 상품 목록 보여줘"*

> VSCode Copilot / Cline / Continue 등록법은 [`../1.dev_helpers/README.md`](../1.dev_helpers/README.md) 와 동일(서버 경로만 이 폴더 `server.py` 로).

## 이런 걸 물어볼 수 있다 (예시 질문)

자연어로 물으면 LLM 이 알맞은 SQL 을 만들어 `run_query` 로 실행한다. 샘플 DB 로 바로 답이 나오는 것들:

| 자연어 질문 | 뒤에서 도는 SQL 개념 |
|-------------|----------------------|
| "테이블 뭐뭐 있어? 각 구조도 보여줘" | `list_tables` + `describe_table` |
| "고객 목록 상위 5명만 보여줘" | 단순 `SELECT ... LIMIT` (`preview_table`) |
| "서울에 사는 고객만 뽑아줘" | `WHERE city='서울'` |
| "취소 뺀 도시별 총 매출은?" | `customers ⋈ orders ⋈ order_items` 3중 조인 + `GROUP BY` |
| "가장 많이 팔린 상품 TOP 3" | 조인 + `SUM(quantity)` + `ORDER BY ... LIMIT` |
| "고객별 주문 건수와 결제액, 많이 쓴 순으로" | `GROUP BY customer` + 정렬 |
| "한 번도 주문 안 한 고객 있어?" | `LEFT JOIN ... WHERE o.id IS NULL` (안티조인) |
| "10만원 넘는 주문만, 고객·금액 같이" | 조인 + `HAVING SUM(...) > 100000` |
| "카테고리별 평균 단가와 재고 합계" | `products` `GROUP BY category` + `AVG`/`SUM` |
| "6월에 결제된 주문 목록" | `WHERE order_date LIKE '2024-06%' AND status='paid'` |
| "부산 고객들이 산 상품 이름들" | 4개 테이블 전부 조인 |

> 팁: **"어떤 테이블/컬럼 있는지 먼저 물어보고"** 시작하면 LLM 이 스키마를 정확히 잡아 더 좋은 SQL 을 만든다.
> (또는 `schema://database` 리소스가 그 지도 역할을 한다.)
>
> ⚠️ 쓰기/삭제 질문(예 *"저 고객 지워줘"*)은 **읽기 전용 가드가 거부**한다 — 이 서버는 조회 전용이다.

## 원격 DB(PostgreSQL / MySQL)로 바꾸기
```bash
cp .env.example .env
# .env 에서 DB_TYPE 을 postgres 또는 mysql 로 바꾸고 접속정보 입력
pip install "psycopg[binary]"     # postgres  (mysql 이면: pip install pymysql)
python client.py                  # 같은 도구로 원격 DB 질의
```
- ★ **읽기 전용 DB 계정**으로 접속하길 권장(코드 가드는 2차 방어).
- 원격은 **TLS** 사용(`server.py` 의 `sslmode`/`ssl` 주석 해제).

---

## 🔐 접속정보는 어디에 저장되고, 안전한가?

### 지금 이 서버 = "로컬 stdio" 모델
- 서버는 **당신 PC에서, 당신 클라이언트가 띄운 자식 프로세스**다. 클라이언트=서버=같은 OS 사용자.
- 그래서 **클라이언트→서버 인증이 없다** — 내 프로세스에 내가 붙는 것이라 신뢰경계가 OS 계정.
- **사용자별 분리도 자동**: 사람이 다르면 PC·`.env`도 각자. A의 `.env`엔 A의 DB, B엔 B의 DB.
- 비밀은 **서버 폴더 `.env`(gitignore, 평문)** 에 있고 서버가 `load_dotenv()` 로 읽는다.
  Claude Code 설정엔 `command/args` 만 넣고 **비밀은 안 넣는다**(중복 저장·유출면 최소화).

> 평문 `.env` 가 불안하면 방어는 "암호화"가 아니라 **최소권한**이다:
> ① 읽기 전용 DB 계정 ② 서버가 SELECT 만 허용(가드 내장) ③ 원격은 TLS ④ `.env` 커밋 금지.
> 인증은 없앨 수 없으니 "털려도 피해 최소화"가 정석.

### 다중 사용자·원격 공유로 확장하려면 (= "원격 shared" 모델)
하나의 서버가 **여러 사용자를 HTTP 로** 서빙한다면 이야기가 달라진다:
1. **클라이언트→서버 인증 필요** — 사용자별 **OAuth/Bearer 토큰** 제시 → 서버가 "이 요청=사용자 A" 식별.
   (아기 버전 데모: [`../../9.projects/2.remote/2.oauth/`](../../9.projects/2.remote/2.oauth/))
2. **"내 계정으로 내 자원 접속"** — 서버가 A의 다운스트림 자격증명을 쓰는 두 방식:
   - **OAuth 패스스루/on-behalf-of**: A가 서버 통해 자기 계정을 직접 인가 → 서버는 A용 **단기 토큰**만 사용(비번 미보유). *claude.ai Gmail/Drive 커넥터가 이 방식.*
   - **서버측 per-user 시크릿 스토어**: `user_id → 자격증명(암호화)` 매핑을 KMS/Vault 에 저장, **토큰으로 인증된 신원에만** 묶어 조회.
3. ⚠️ **혼동된 대리인(confused deputy)** 주의 — 공유 서버가 모두의 비밀을 쥐면, A 요청이 B 자격증명을 쓰지 않도록 **다운스트림 조회를 반드시 '인증된 user_id'에만 바인딩**(요청 본문·LLM 이 말한 값으로 고르지 말 것).

| | 로컬 stdio (이 서버) | 원격 shared |
|---|---|---|
| 클라이언트→서버 인증 | 없음(내 프로세스) | 필요(OAuth/Bearer) |
| per-user 자격증명 | 각자 자기 `.env` | 토큰→user_id→스토어/패스스루 |
| 예시 | sql-helper, dev-helper, Playwright | claude.ai Gmail/Drive |

---

## 🧩 설계 메모: 왜 `server.py` 하나인가 (DB별로 안 쪼갠 이유)

DB 3종을 지원하지만 파일은 **하나로 유지**했다. `server_sqlite.py` / `server_mysql.py` / `server_postgres.py`
로 쪼개지 **않는다.** 이유는 "무엇이 공유되고 무엇이 다른가" 다:

- **공유(코드의 대부분)**: 도구 정의(`list_tables`/`describe_table`/`run_query`), **읽기 전용 가드**,
  결과 포맷팅 — 제일 까다롭고 가치 있는 부분이 3종 DB 에서 **완전히 동일**하다.
- **다른 것(소수)**: `connect()` 커넥션 팩토리 + introspection SQL 몇 줄 + 식별자 인용. 전체의 10% 남짓.

→ DB별 풀-서버로 쪼개면 그 **가드·포맷 로직이 3벌로 복제**된다. 가드 버그 하나가 3곳 수정이 되고
시간이 지나면 셋이 어긋난다. **분리 축은 "DB별"이 아니라 "레이어별"** 이어야 한다:

```
server.py     ← MCP 도구 + 가드 + 포맷 (한 벌, DB 무관)
dialects.py   ← DB별로 다른 것만: connect() / introspection / 인용   ← 커지면 이때 추출
```

지금 `server.py` 는 이 구조를 **한 파일 안 섹션**(`1)연결 · 2)스키마 · 3)가드 · 4)도구`)으로 담았다.
파일이 작을 땐 굳이 나눌 필요도 없다.

**언제 쪼개나(신호)**
- dialect 코드가 커질 때(타입 매핑·페이지네이션·DB 고유 기능) → `dialects/` 패키지로 **추출**. 단 **MCP 진입점은 여전히 하나**.
- DB마다 **도구 자체가 달라질 때**(예: postgres 전용 기능 노출) → 그때 비로소 서버 분리 고려.

**운영 관점**에서도 한 파일이 낫다: 클라이언트엔 **서버 하나만 등록**하고 `.env` 의 `DB_TYPE` 로 대상만 바꾼다.
3개로 쪼개면 `sql-sqlite`/`sql-mysql`… 세 개를 등록해야 하고, 똑같은 도구가 3벌로 보여 지저분하다.

> 일반론: 실무 MCP 서버도 대개 **작고 단일 모듈**이 정석(공식 filesystem·git 서버 등). 다중 파일은 "진짜 커졌을 때"의 선택.

## 다음 / 관련
- **인증이 얽히는 실전 3모델** → [`../3.sql_helpers_auth/`](../3.sql_helpers_auth/) (서버관리 / 사용자별 스코프 / 클라이언트 제공)
- 등록 흐름 익히기 → [`../1.dev_helpers/`](../1.dev_helpers/)
- 원격 인증 데모 → [`../../9.projects/2.remote/2.oauth/`](../../9.projects/2.remote/2.oauth/)
- 읽기 전용 가드는 2차 방어일 뿐 — 운영 DB 는 반드시 최소권한 계정으로.
