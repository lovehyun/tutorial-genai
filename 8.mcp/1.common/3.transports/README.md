# 1.common/3.transports — stdio vs HTTP 전송

지금까지 예제는 모두 **stdio**(클라이언트가 서버를 자식 프로세스로 실행)였다.
여기선 같은 서버를 **HTTP** 로 띄우고 네트워크로 붙는다 — 상시/원격 서버의 출발점.

## 파일
- `server_http.py` — `mcp.run(transport="streamable-http")` → `http://localhost:8000/mcp`
- `1.client_http.py` — `streamablehttp_client("http://localhost:8000/mcp")` 로 접속

## 실행 (⚠️ stdio 와 달리 **서버를 먼저** 띄워야 함 — 터미널 2개)
```bash
pip install mcp

# 터미널 1 — 서버 먼저 (계속 떠 있음)
cd 8.mcp/1.common/3.transports
python server_http.py        # localhost:8000 에서 대기

# 터미널 2 — 클라이언트
cd 8.mcp/1.common/3.transports
python 1.client_http.py      # 실행 중인 서버에 HTTP 로 접속
```

## 관전 포인트
- **stdio vs HTTP 의 본질 차이**:
  - stdio = 클라이언트가 서버를 띄움(자동, 1:1, 로컬). 2.server_quickstart 가 이것.
  - HTTP = 서버가 독립 실행(수동 선실행) → **여러 클라이언트 / 원격 접속** 가능.
- 클라이언트 코드 차이는 접속부 한 줄뿐: `stdio_client(...)` → `streamablehttp_client(url)`.
  나머지(`initialize` / `list_tools` / `call_tool`)는 **완전히 동일**.
- 원격 배포로의 확장은 [`../../9.projects/2.remote/`](../../9.projects/2.remote/) 로 이어진다.
