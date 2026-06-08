# 1.common/2.protocol_deep — MCP 프로토콜 깊게 보기

`1.intro` 에서 첫 왕복을 했다면, 여기서는 **프로토콜 내부와 더 많은 기능**을 본다:
도구 여러 개, **resource·prompt 발견**, 그리고 **오가는 JSON-RPC 를 눈으로** 확인한다.

## 학습 순서

| 단계 | 파일 | 무엇을 보나 |
|---|---|---|
| 1 | `1.simple_server.py` | 도구 몇 개를 가진 서버 |
| 2 | `2.simple_client.py` | 도구 호출 + **`debug_proxy` 경유로 오가는 JSON-RPC 출력** |
| 2 | `2.simple_client2_tryexcept.py` | 2 + 예외 처리 |
| 3 | `3.simple_server2.py` | tools + **resources + prompts** 를 가진 서버 |
| 4 | `4.simple_client3_getinfo.py` | 서버의 **tools / resources / prompts 전체 발견** (`list_resources`, `get_prompt`) |
| 4 | `4.simple_client3_getinfo2_tryexcept.py` | 4 + 예외 처리 |
| 5 | `5.server_tools_resource.py` | tools 여러 개 + resource(`info://server`) 를 가진 서버 |
| 6 | `6.client_tools_resource.py` | **`call_tool`(실행) vs `read_resource`(읽기)** 를 직접 비교 — tool/resource 차이 |
| — | `debug_proxy.py` | (유틸) 클라↔서버 JSON-RPC 를 로그로 중계하는 디버거 |

> `_tryexcept` = 같은 예제 + 예외 처리 (번호 공유). 서버↔클라 짝: **1↔2, 3↔4, 5↔6**.
> (`5.server_tools_resource.py` 는 [`../../4.langchain/1.quickstart/1.agent.py`](../../4.langchain/1.quickstart/) 가 LLM 클라이언트로도 재사용한다 — "서버 하나, 클라 여럿".)

## 실행
```bash
pip install mcp
cd 8.mcp/1.common/2.protocol_deep
python 2.simple_client.py              # debug_proxy 경유 → 1.simple_server 호출, 프로토콜 메시지 출력
python 4.simple_client3_getinfo.py     # tools/resources/prompts 발견
python 6.client_tools_resource.py      # call_tool(실행) vs read_resource(읽기) 비교
```

### MCP Inspector 로 클릭 테스트 (Node 필요)
```bash
pip install "mcp[cli]"
mcp dev 5.server_tools_resource.py     # 브라우저 UI 에서 tool/resource 직접 호출
```

## 다음 단계
- **[`../3.transports/`](../3.transports/)** — stdio → HTTP 전송
- LLM 자동 호출 → [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/) (이 폴더의 `5.server_tools_resource.py` 를 어댑터가 그대로 재사용)
