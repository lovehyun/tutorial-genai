# 3.anthropic/1.claude_desktop/2.simple_net_local — 로컬 stdio 네트워크 진단 서버

`1.mcp_hello`의 인사 도구 하나짜리 서버보다 한 단계 실용적인 예제 — **네트워크 진단 도구**를
Claude Desktop에 등록해서 실제로 쓸모 있는 걸 만들어본다. `3.simple_net_remote/`가 같은 도구를
Docker+Nginx로 원격 배포하는 버전이라면, 여기는 **로컬 stdio**(가장 단순한 등록 방식)다.

## 파일
- `simple_net_check.py` — 도구 3개짜리 MCP 서버

| 도구 | 기능 |
|---|---|
| `ping_host(host, count, timeout_sec)` | ICMP ping 실행, 원문 결과 반환 |
| `check_common_ports(host, timeout_sec)` | 주요 포트(22/80/443/3000/5000/8000) 열림/닫힘 동시 확인 |
| `fetch_page(host, port, path, max_bytes)` | 포트 80/5000 한정 간단 HTTP GET |

## Claude Desktop 등록
`claude_desktop_config.json`에 추가(절대경로 사용):
```json
{
  "mcpServers": {
    "simple-net-local": {
      "command": "python",
      "args": ["C:/절대경로/tutorial-genai/5.mcp/3.anthropic/1.claude_desktop/2.simple_net_local/simple_net_check.py"]
    }
  }
}
```
등록 후 Claude Desktop을 재시작하면 도구 패널에 `simple-net-local`이 나타난다.

## 관전 포인트
- **`fetch_page`가 포트 80/5000만 허용**하도록 화이트리스트 처리된 걸 눈여겨볼 것 — 사람이 자연어로
  아무 포트나 요청해도 도구 자체가 범위를 제한한다(모델의 판단에만 기대지 않는 방어).
- `check_common_ports`는 `asyncio.gather`로 6개 포트를 **동시에** 확인 — MCP 도구 안에서도 일반
  비동기 코드를 그대로 쓴다.
- stdout에 `print()`를 쓰지 않고 `logging`을 `stderr`로 명시 — stdio 전송에서 stdout은
  JSON-RPC 채널이라 오염되면 안 된다(`1.basic/README.md`의 공통 원칙).

## 다음 단계
- 같은 서버를 **원격**(Docker+Nginx+TLS)으로 배포 → [`../3.simple_net_remote/`](../3.simple_net_remote/)

## 설치
```bash
pip install "mcp[cli]"
```
