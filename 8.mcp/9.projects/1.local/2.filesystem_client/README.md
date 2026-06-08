# 2.filesystem_client — 같은 서버, 여러 클라이언트 (자연어 파일 작업)

[`../1.filesystem`](../1.filesystem) 의 MCP 파일 서버에 붙는 **세 가지 클라이언트**.
서버는 그대로 두고 클라이언트만 바꿔 **"서버 하나, 클라 여럿"** 을 보여준다.

| 파일 | 방식 | 설명 |
|---|---|---|
| `1.fs_mcp_client.py` | GPT function calling | 자연어 → 알맞은 MCP 파일 도구 자동 호출 (정해진 질문 배치) |
| `2.fs_mcp_client2_config.py` | + `config.json` | 서버 경로·데모 질문을 설정 파일에서 읽음 |
| `3.fs_mcp_client3_gpt.py` | 대화형 | 멀티턴 — 직접 명령 입력 (quit 종료) |

## 실행
```bash
pip install mcp langchain-openai openai python-dotenv
# 키: 8.mcp/.env 또는 이 폴더 .env 에 OPENAI_API_KEY
python 1.fs_mcp_client.py
```
> 셋 다 `../1.filesystem/server/server.py`(4툴)를 자식 프로세스로 띄운다(`cwd`로 workspace 지정).

## 관전 포인트
- 서버(`1.filesystem`)는 손대지 않고 **클라이언트만 기본/config/대화형으로 교체** — MCP 재사용성.
- 자연어를 OpenAI function calling 으로 받아 `list_files`/`read_file`/`copy_file` 중 **자동 선택**.
