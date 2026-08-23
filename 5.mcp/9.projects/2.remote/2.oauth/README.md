# 2.oauth — 원격 MCP 서버에 인증 붙이기 (Bearer 토큰)

[`../1.intro/`](../1.intro/) 의 원격 서버는 **URL 만 알면 누구나** 붙는다. 실전 원격 서버는 그럴 수 없다.
여기서는 streamable-http 앱 앞에 **Bearer 토큰 검사 미들웨어**를 끼워, 올바른 토큰을 실은 요청만 통과시킨다.

```
클라이언트 ──[Authorization: Bearer <TOKEN>]──▶  미들웨어  ──▶ MCP 서버
                              토큰 없음/틀림 ──▶ 401 Unauthorized
```

> **stdio→HTTP** 때 클라이언트 접속부가 딱 한 줄 바뀌었듯, **인증도 `headers` 한 줄**이 전부다.

## 파일
| 파일 | 무엇을 |
|---|---|
| `server.py` | `mcp.streamable_http_app()` + `BearerAuthMiddleware` → uvicorn 실행 |
| `client.py` | ①토큰 없이(거부) ②Bearer 토큰(성공) 두 번 접속해 차이를 보여줌 |
| `.env.example` | `MCP_SERVER_URL`, `MCP_API_TOKEN` 템플릿 → `.env` 로 복사해 사용 (복사 안 해도 코드 기본값으로 동작) |

## 실행 (터미널 2개)
```bash
pip install mcp uvicorn python-dotenv     # 또는: pip install -r ../../../requirements.txt
# (선택) cp .env.example .env             # 토큰/URL 바꾸려면

# 터미널 1 — 서버
cd 5.mcp/9.projects/2.remote/2.oauth
python server.py            # http://127.0.0.1:8000/mcp  (Bearer 필요)

# 터미널 2 — 클라이언트
cd 5.mcp/9.projects/2.remote/2.oauth
python client.py            # 무토큰=거부, 유토큰=성공 을 순서대로 확인
```

## 관전 포인트
- 서버는 `mcp.run(...)` 대신 **`mcp.streamable_http_app()` 로 Starlette 앱을 꺼내** 미들웨어를 끼우고 uvicorn 으로 띄운다.
- `/mcp` 경로만 보호하고 헬스체크 등은 열어둘 수 있다(미들웨어 안 분기).
- 클라이언트는 `streamablehttp_client(URL, headers={"Authorization": f"Bearer {TOKEN}"})`.
- 토큰은 코드에 박지 말고 `.env`/환경변수/시크릿 매니저에서.

## ⚠️ 범위 — 이건 '정적 토큰' 최소 예제
실제 프로덕션의 완전한 MCP 인증은 **OAuth 2.1** 을 쓴다:
- **Protected Resource Metadata**(`/.well-known/oauth-protected-resource`) 로 인증 서버 위치 공개
- 클라이언트가 **동적으로 토큰 발급**받아 요청, 서버가 **서명·스코프·만료 검증**

이 예제는 "인증이 **왜/어디에** 끼는지" 를 먼저 눈으로 익히는 용도다. 다음 단계 참고:
- MCP 인증 스펙: <https://modelcontextprotocol.io/specification/basic/authorization>
- Python SDK 의 `mcp.server.auth`(TokenVerifier / OAuth 리소스 서버) 예제

## 관련
- 무인증 원격: [`../1.intro/`](../1.intro/)
- Docker/nginx 배포: [`../../../3.anthropic/1.claude_desktop/3.simple_net_remote/`](../../../3.anthropic/1.claude_desktop/3.simple_net_remote/) (리버스 프록시 계층에서 인증을 얹는 방법도 있음)
