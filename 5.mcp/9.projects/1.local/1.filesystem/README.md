# 1.filesystem — 파일시스템 MCP 서버 + 클라이언트

파일 작업(목록/읽기/쓰기/검색…)을 **MCP 서버**로 만들고 클라이언트로 호출한다.
모든 작업은 서버의 `workspace/` 폴더 안에서만 일어난다(디렉토리 탈출 방지).

## 구성
| 파일 | 설명 |
|---|---|
| `server/server.py` | **간단 서버 (4툴)** — list_files / read_file / rename_file / copy_file |
| `server/server2.py` | **고급 서버 (9툴)** — + write / create_directory / delete / move / search / get_file_info (보안 강화) |
| `client/client.py` | 간단 클라 — 번호 메뉴로 `server.py` 호출 |
| `client/client2.py` | 고급 클라 — `server2.py`(9툴) 자동 데모 + 대화형 셸 |
| `workspace/` | 작업 폴더 (hello.txt, sample.txt, test.txt) |

## 실행 (반드시 `1.filesystem` 폴더에서)
```bash
pip install mcp
python client/client.py      # 간단 (4툴 메뉴: 1~5)
python client/client2.py     # 고급 (9툴: 1=자동 데모 / 2=대화형 셸)
```
> 클라이언트가 server 를 **자식 프로세스(stdio)로 자동 실행**한다. (LLM 불필요)

## 관전 포인트
- 같은 파일 작업을 **server.py(4툴) → server2.py(9툴)** 로 확장 = "함수만 추가하면 도구가 는다".
- `client.py` / `client2.py` 가 **같은 폴더의 서버**에 붙는다 — 클라만 바꿔도 동작.
- GPT/자연어/config 기반 다른 클라이언트는 → [`../2.filesystem_client/`](../2.filesystem_client/)
