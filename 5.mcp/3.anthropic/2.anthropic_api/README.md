# 3.anthropic/2.anthropic_api — Claude API로 MCP 도구 쓰기 (도구 선택: 수동 → 키워드 → LLM)

`1.claude_desktop/`이 **Claude Desktop 앱에 설정 파일로 등록**하는 법이었다면, 여기는 **코드로
Anthropic API가 직접 MCP 서버를 호출**하는 법이다 — `2.openai/1.agent_tool/`과 완전히 대칭되는
구조. 하나의 MCP 서버를 두고, 클라이언트가 어떤 도구를 부를지 고르는 방식을 수동→키워드→LLM
순으로 고도화한다.

## 파일
- `server.py` — `2.openai/1.agent_tool/server.py`와 **완전히 같은 도구 3개**(hello, add, now)

| 클라이언트 | 도구 선택 방식 |
|---|---|
| `1.client_demo.py` | 수동(도구 목록 + 하드코딩 호출) — `2.openai`판과 코드 100% 동일 |
| `2.client_manual_nlp.py` | 키워드/정규식 매칭 — `2.openai`판과 코드 100% 동일 |
| `3.client_claude.py` | **Claude tool_use 자동 선택** — 여기서부터 벤더가 갈린다 |

## 실행
```bash
cd 5.mcp/3.anthropic/2.anthropic_api
pip install mcp anthropic python-dotenv
# .env 에 ANTHROPIC_API_KEY  (3번 파일만 필요)

python 1.client_demo.py         # 서버 자동 실행 → 도구 목록 + 정해진 호출
python 2.client_manual_nlp.py   # 입력을 키워드로 매칭해 도구 선택
python 3.client_claude.py       # 자연어 → Claude 가 도구/인자 선택
```

## 왜 1·2번은 두 벤더 폴더에 코드가 똑같이 들어있나

LLM이 아직 등장하지 않는 단계(수동 하드코딩, 키워드 매칭)에는 애초에 "벤더"라는 개념이 없다.
`2.openai/1.agent_tool/1~2`와 이 폴더의 `1~2`가 한 글자도 안 다른 게 정상이다 — **벤더 차이는
LLM이 등장하는 순간(`3.client_gpt.py` ↔ `3.client_claude.py`)부터 시작된다**는 걸 코드 중복
자체로 보여주려는 의도다.

## 관전 포인트 — `3.client_gpt.py`와 나란히 비교

| | OpenAI(`2.openai/1.agent_tool/3.client_gpt.py`) | Claude(`3.client_claude.py`) |
|---|---|---|
| 스키마 필드명 | `inputSchema` → `parameters`(camelCase 그대로) | `inputSchema` → `input_schema`(snake_case로 변환) |
| 도구 선택 신호 | `msg.tool_calls` 존재 여부 | `resp.stop_reason == "tool_use"` |
| 결과 되돌리기 | `role: "tool", tool_call_id` | `type: "tool_result", tool_use_id` |
| 여러 도구 동시 호출 | `tool_calls` 리스트 | `content` 안의 `tool_use` 블록 여러 개 |

**서버(`server.py`)는 완전히 같다** — 바뀌는 건 "MCP 도구 스키마를 어느 벤더 형식으로 감싸는가"와
"그 벤더의 도구 호출 프로토콜을 어떻게 처리하는가"뿐이다. `4.langchain/1.quickstart/`가 이
변환을 자동으로 해주는 어댑터라는 것도, 이 두 파일을 직접 비교해봐야 그 가치가 보인다.

## 추천 순서
`1.client_demo` → `2.client_manual_nlp` → `3.client_claude`
→ (비교) [`../../2.openai/1.agent_tool/`](../../2.openai/1.agent_tool/)
→ (재시도까지 보고 싶다면) [`../../2.openai/1.agent_tool/4.client_gpt3_retry.py`](../../2.openai/1.agent_tool/4.client_gpt3_retry.py)
