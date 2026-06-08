# 4.chatbot_web — 웹 챗봇 × LangChain 에이전트 × MCP

브라우저 채팅창에서 자연어로 물으면, **LangChain 에이전트가 MCP 서버의 도구를 자동으로 골라** 답한다.
*"내 기능을 MCP 서버로 만들면, 웹앱이든 어디든 에이전트가 그대로 쓴다"* 를 보여주는 작은 실전 예제.

## 구성
| 파일 | 역할 |
|---|---|
| `server.py` | **MCP 서버** — `calculator` / `now` / `roll_dice` / `weather` (도구 4개) |
| `app.py` | **Flask 백엔드** — MCP 도구를 `get_tools()`로 받아 `create_agent`, `/chat` 엔드포인트 |
| `templates/index.html` | 채팅 UI (답변 + **사용한 도구** 표시) |

## 흐름
```
브라우저 ──"12*7?"──▶ Flask /chat ──▶ create_agent(LLM + MCP 도구)
                                          │ 에이전트가 calculator 선택
                                          ▼
                          MCP server.py(calculator) → "84" → "84입니다"
```

## 실행
```bash
pip install flask langchain-openai langchain-mcp-adapters langgraph python-dotenv
# OPENAI_API_KEY 설정 (.env 또는 8.mcp/.env)
python app.py        # → http://localhost:5050
```
채팅창에 *"12 * 7 은?"*, *"지금 몇 시?"*, *"주사위 굴려줘"*, *"서울 날씨"* 입력 → 답변과 **🛠 사용한 도구** 표시.

## 관전 포인트
- 웹앱은 **MCP 프로토콜만** 알면 됨 — `server.py` 도구가 늘면 챗봇 능력도 자동으로 는다.
- 같은 `server.py` 를 Claude Desktop·VSCode·CLI 어디에 붙여도 동작 (MCP 재사용성).
- 더 강력하게: `server.py` 대신 [`../3.codebase_qa/server.py`](../3.codebase_qa/)(RAG)를 붙이면 **"내 문서 QA 챗봇"** 이 된다.
