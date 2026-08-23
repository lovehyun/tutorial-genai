# 11.agent_sdk — Claude Agent SDK

`Claude Code`를 구동하는 것과 **같은 에이전트 루프**를 파이썬 코드로 그대로 씁니다
(2025년 말 "Claude Code SDK"에서 "Claude Agent SDK"로 개명). `2.tools`가 `anthropic` SDK로
직접 도구 호출 루프를 짜는 것이라면, 이건 그 루프 자체(권한 관리·MCP·훅·서브에이전트 포함)를
이미 완성된 형태로 가져다 쓰는 것입니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.hello_query.py` | 가장 단순한 호출 — `query()`, 안전장치(도구 없음·비용 상한) |
| `2.streaming_messages.py` | 메시지 스트림의 종류(System/Assistant/Result) 이해하기 |
| `3.custom_tool.py` | `@tool` + `create_sdk_mcp_server`로 내 함수를 도구로 등록 |

## ⚠️ 먼저 읽을 것 — 가벼운 API 호출이 아닙니다

이 SDK는 `anthropic` SDK처럼 "메시지 하나 보내고 답 받기"가 아니라, **Claude Code 전체
에이전트를 하나 띄우는 것**입니다. 실제로 확인된 차이:

| | `anthropic` SDK (1.basic 등) | Claude Agent SDK |
|---|---|---|
| 인증 | `.env`의 `ANTHROPIC_API_KEY` | **이 컴퓨터에 로그인된 Claude Code CLI 인증** |
| 기본 도구 | 없음(직접 선언) | Read/Write/Bash 등 **Claude Code 전체 툴셋**이 기본 포함 |
| 시스템 프롬프트 | 내가 짧게 작성 | Claude Code 기본 프롬프트(방대함) — 캐시 생성 토큰만 수만 개 |
| 비용 (동일 질문 "2+2는?") | 거의 0원 | 기본 설정 시 **$0.11**, `tools=[]`+커스텀 프롬프트로 줄이면 **$0.008~0.03** |

그래서 이 폴더의 모든 예제는 `tools=[]`(또는 필요한 도구만) + 짧은 커스텀 `system_prompt` +
`max_budget_usd`(비용 상한)를 기본으로 켜뒀습니다. 실전에서 기본값 그대로 쓰면 의도치 않게
파일을 읽고 쓰는 등 강력한 권한이 켜진 채로 실행됩니다.

## 사전 준비

```bash
pip install claude-agent-sdk anyio
```

- Python 3.10+
- `claude` CLI가 설치·로그인돼 있어야 합니다(이 저장소를 Claude Code로 보고 있다면 이미 준비된 상태).
- `.env`의 `ANTHROPIC_API_KEY`는 **여기선 쓰이지 않습니다** — CLI 로그인 인증을 그대로 씁니다.

## 다른 에이전트 프레임워크와 비교

| | 프레임워크 | 도구 등록 방식 | 특징 |
|---|---|---|---|
| `2.langchain/8.agents` | LangChain | `@tool` (LangChain 전용) | 벤더 중립, 생태계가 넓음 |
| `5.mcp/` | MCP 프로토콜 | 독립 프로세스(MCP 서버) | 어떤 클라이언트에서든 재사용 가능 |
| `11.agent_sdk`(여기) | Claude Agent SDK | `@tool` + 내 프로세스 안 MCP 서버 | Claude Code와 완전히 같은 루프, Anthropic 네이티브 |

`3.custom_tool.py`는 사실 "내 프로세스 안에서 도는 초소형 MCP 서버"를 만드는 것이라
`5.mcp`와 개념이 이어집니다 — 진짜 독립 프로세스 MCP 서버를 붙이는 법은
[`../../5.mcp/4.langchain/`](../../5.mcp/4.langchain/) 참고.
