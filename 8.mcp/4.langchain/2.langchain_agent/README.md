# 4.langchain/2.langchain_agent — MCP 도구를 LangChain 도구로 감싸기 (수동 변환)

MCP 도구를 LangChain `Tool`/`@tool` 로 **직접 감싸** `create_agent` 가 쓰게 한다.
`1.quickstart` 는 `langchain-mcp-adapters` 가 이 변환을 자동으로 해주는데, 여기선 손으로 해보며 원리를 본다.

## 파일
- `server.py` — say_hello 1개 / `server2.py` — say_hello·add·now·multiply·get_day_of_week
- `1.1_client1_pydantic.py` — Pydantic `BaseTool` 로 감싸 직접 호출 (server.py)
- `1.2_client1_simple_function.py` — 함수 + `Tool(coroutine=...)` + ReAct 에이전트
- `1.3_..._simple_function2_exception.py` — + 예외 처리
- `1.4_client1_multi_tools.py` — 여러 도구로 확장하는 패턴(새 도구 = 함수 + 목록 추가)
- `1.5_..._multi_tools2_exception.py` — 멀티 도구 + 예외 처리
- `2.2_client2_async_sync.py` — `.invoke()`(동기) vs `.ainvoke()`(비동기) 비교 (server2.py)

## 실행
```bash
cd 8.mcp/4.langchain/2.langchain_agent     # 상대경로 server.py 사용 → 폴더 안에서 실행
pip install mcp langchain langchain-openai langchain-core python-dotenv
# .env 에 OPENAI_API_KEY

python 1.1_client1_pydantic.py
python 1.2_client1_simple_function.py
python 1.4_client1_multi_tools.py
python 2.2_client2_async_sync.py           # 실행 시 sync/async 선택
```
> 클라이언트가 `server.py`(2.2 는 `server2.py`)를 stdio 로 **자동 실행**.

## 관전 포인트
- **MCP 도구 → LangChain Tool 수동 변환** — adapters(1.quickstart)가 대신 해주던 일을 직접 → 어댑터의 가치를 체감.
- `1.2`~`1.5` 는 도구 호출마다 `asyncio.run` 으로 이벤트 루프를 만든다 → **async 경계**가 어디인지 관찰.
- `2.2` 로 동기/비동기 실행 경로 비교.

## 추천 순서
`1.1` → `1.2` → `1.3` → `1.4` → `1.5` → `2.2`
