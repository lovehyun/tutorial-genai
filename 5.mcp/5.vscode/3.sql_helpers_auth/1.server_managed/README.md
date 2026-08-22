# 케이스 1 — 서버가 자격증명을 다 관리 (모두 동일 접근)

```
클라이언트 ──(신원 불필요)──▶ 서버 ──[.env 자격증명으로 로그인]──▶ DB
```

- 서버 `.env` 에 접속정보가 있고, `connect()` 가 그 값으로 DB 에 **인증**한다.
- 누가 부르든 **같은 계정**으로 붙는다 → 모두 동일 권한. (사내 대시보드 백엔드 같은 형태)
- **"원격 DB 인증을 실제로 어떻게 하냐"의 답**이 여기 산다 — [server.py](server.py) 의 `connect()` 가
  sqlite / postgres / mysql / 접속URL / 클라우드 IAM 을 전부 보여준다.

## 실행 (sqlite 데모)
```bash
python ../init_db.py            # shop.db 생성
pip install mcp python-dotenv
cd 1.server_managed
python client.py                # 붙어서 조인 질의 (신원 제시 없음)
```

## 실제 원격 DB 인증은? (`.env` 만 바꾸면 됨)
| 상황 | 당신이 하는 것 |
|------|----------------|
| 자체호스팅 PG/MySQL | `.env` 에 host/user/password |
| 관리형(Supabase/Neon/RDS) | 위 + **SSL**(`PGSSLMODE=require`) 또는 `DATABASE_URL` 통째로 |
| 클라우드 IAM(AWS 등) | 비번 대신 **클라우드 크레덴셜** → `connect()` 에서 단기 토큰 발급 |
| 폐쇄망 | **SSH 터널** 후 `PGHOST=localhost` |

> 핵심: 서버가 DB 에 붙는 건 **평범한 앱이 DB 붙는 것과 똑같다**. `.env`(또는 클라우드 크레덴셜)에
> 정보를 넣으면 `connect()` 가 로그인. MCP 는 그 위에 도구로 노출만 얹은 것.
> ★ 운영은 **읽기 전용 계정** + TLS 권장. `.env` 는 gitignore(커밋 금지).

## 언제 이 모델이 맞나 / 한계
- ✅ 모든 사용자가 같은 데이터를 봐도 되는 경우(공용 대시보드, 사내 통계).
- ❌ 사용자마다 다른 데이터/권한이 필요하면 → **케이스 2** (호출자 인증 + 스코프).
