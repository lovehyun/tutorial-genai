# MCP 유연 포맷 커리큘럼 (시간 포맷별 모듈 조합)

## 과정 정보
- **기간**: 유연 — 4시간 / 8시간(원데이) / 16시간(2일), 3개 포맷 중 상황에 맞게 선택
- **난이도**: 입문~중급
- **대상**: 강사가 청중·가용 시간에 맞춰 포맷을 고르는 용도. 파일명까지 못박은 정식 3일 심화 과정은 [`3.advanced/1.mcp_protocol_deep_dive`](../../3.advanced/1.mcp_protocol_deep_dive/) 참고
- **선수 과목**: LLM tool-calling/에이전트 개념을 한 번은 접해본 사람(복습으로 다시 훑는다). 완전 초심자면 [`2.intermediate/2.agent_development`](../../2.intermediate/2.agent_development/) 선행 권장

같은 교재([`8.mcp/`](../../../8.mcp/))로 **수업 길이·일수**에 맞춰 짜는 커리큘럼 모음.
**모듈(레고 블록)** 을 먼저 정의하고, **시간 포맷**(4H / 8H / 16H×2day)별로 조합한다.

> 형식 표기 — **데모**: 강사 실행·수강생 관찰 / **핸즈온**: 직접 타이핑 / **강의**: 설명 중심(코드 없음)


============================================================
## 0. 모듈 카탈로그 (레고 블록)
============================================================

각 포맷은 아래 모듈을 골라 붙인 것. "표준분량"은 데모+짧은 핸즈온 기준(±10분 조절).

| ID | 모듈 | 폴더 | 표준분량 | 핵심 |
|----|------|------|---------|------|
| **M0** | 오리엔테이션 | [8.mcp/README.md](../../../8.mcp/README.md) | 10m | MCP=도구↔LLM의 USB, 왜/무엇 |
| **M0.5a** | llm-math 호출(빌트인) | [2.langchain/8.agents/1.builtin_tools](../../../2.langchain/8.agents/1.builtin_tools/) (`1.0_list_all_tools.py`, `1.1_llm_math.py`) | 10m | 이미 만들어진 Calculator 도구를 현행 `create_agent`로 부르기만 |
| **M0.5b** | llm-math 직접 만들기 | [2.langchain/8.agents/2.custom_tools](../../../2.langchain/8.agents/2.custom_tools/) (`2.2_at_tool_basic.py`) | 15m | `@tool` 데코레이터로 계산 도구(`calculate_tip`)를 손으로 제작. docstring·타입힌트가 LLM이 읽는 명세임을 확인 → "근데 이 도구, LangChain 프로세스 밖에선 못 쓴다" → MCP로 브릿지 |
| **M1** | 프로토콜 첫 접촉 | [8.mcp/1.basic/1.intro](../../../8.mcp/1.basic/1.intro/) | 30m | 첫 왕복 `initialize→list_tools→call_tool` |
| **M2** | 프로토콜 심화 | [8.mcp/1.basic/2.protocol_deep](../../../8.mcp/1.basic/2.protocol_deep/) | 40m | tool/resource/prompt · **debug_proxy로 JSON-RPC** |
| **M3** | 전송 | [8.mcp/1.basic/3.transports_http](../../../8.mcp/1.basic/3.transports_http/) | 25m | stdio ↔ HTTP(streamable) |
| **M4** | 양방향·Context | [8.mcp/1.basic/4.advanced](../../../8.mcp/1.basic/4.advanced/) | 50m(핵심 25m) | sampling·progress·elicitation·roots + 지속세션/양방향 |
| **M5** | LLM 자동호출(LangChain) | [8.mcp/4.langchain/1.quickstart](../../../8.mcp/4.langchain/1.quickstart/) | 40m | 어댑터로 에이전트가 도구 자동 선택 |
| **M6** | LLM 자동호출(OpenAI) | [8.mcp/2.openai](../../../8.mcp/2.openai/) | 35m | GPT function calling, 수동→자동 |
| **M7** | LangChain 심화 | [8.mcp/4.langchain](../../../8.mcp/4.langchain/) | 145m | 수동변환·LangGraph 브릿지·도구 안전성 + 원격 HTTP/실전 API 서버 + 사람 승인(HITL) + 가드레일(인젝션·PII·악성 서버) |
| **M8** | 클라이언트 등록 | [8.mcp/5.vscode/1.dev_helpers](../../../8.mcp/5.vscode/1.dev_helpers/) + [운영가이드](../../../8.mcp/claude_code_mcp_guide.md) | 45m | `.mcp.json`/`.vscode/mcp.json`/`claude mcp add` |
| **M9** | DB 자연어 질의 | [8.mcp/5.vscode/2.sql_helpers](../../../8.mcp/5.vscode/2.sql_helpers/) | 45m | 자연어→조인 SQL · read-only 가드 |
| **M10** | DB 인증 3모델 | [8.mcp/5.vscode/3.sql_helpers_auth](../../../8.mcp/5.vscode/3.sql_helpers_auth/) | 60m | 서버관리 / 사용자별 스코프 / 클라 제공 |
| **M11** | 원격 배포·인증·TLS | [8.mcp/9.projects/2.remote](../../../8.mcp/9.projects/2.remote/) | 45m | HTTP 원격 · Bearer/OAuth · http→https·mTLS |
| **M12** | RAG를 MCP로 | [8.mcp/9.projects/3.codebase_qa](../../../8.mcp/9.projects/3.codebase_qa/) | 40m | `search`/`answer` 서버, 멀티 클라 재사용 |
| **M13** | 실전 프로젝트 | [8.mcp/9.projects](../../../8.mcp/9.projects/) (1.local·5.chatbot_web·6.multi_mcp_concierge) | 60m | filesystem·챗봇·멀티MCP 컨시어지 |
| **M14** | 클라이언트 운영 | [claude_code_mcp_guide](../../../8.mcp/claude_code_mcp_guide.md) | 30m | 서버 출처·상태·login/reconnect |
| **M15** | 미니 프로젝트/종합 | (자유) | 60m | 내 도구/DB를 MCP로 만들어 붙이기 |
| **M16** | 여러 MCP 서버 라우팅 | [8.mcp/2.openai/2.multi_tools](../../../8.mcp/2.openai/2.multi_tools/) | 35m | 서버 2개 동시 연결 · 키워드→LLM 라우팅 (단독→매뉴얼→LLM 라우팅 3단 고도화) |
| **M19** | mcp-math 로컬 연동(stdio) | [8.mcp/2.openai/2.multi_tools/math_server.py](../../../8.mcp/2.openai/2.multi_tools/math_server.py) | 15m | `llm-math`와 같은 계산 개념을 **MCP 서버**로 — 클라이언트가 stdio로 자식 프로세스로 띄워 호출 |
| **M20** | mcp-math 원격 연동(HTTP) | [8.mcp/4.langchain/5.remote_http/1.server_simple.py](../../../8.mcp/4.langchain/5.remote_http/1.server_simple.py) | 15m | 같은 `add` 도구, `mcp.run()` 딱 한 줄만 바뀌어 원격 HTTP로 접속 — 도구 정의는 완전히 동일 |
| **M17** | 실전 순차·분기(멀티 컨시어지) | [8.mcp/9.projects/6.multi_mcp_concierge](../../../8.mcp/9.projects/6.multi_mcp_concierge/) | 40m | 쇼핑몰+여행사 두 외부 서버를 한 챗봇이 오가며 순차 처리. ⚠️ "조건 분기"만 떼어 보여주는 순수 예제는 레포에 없음 — 이 실전 흐름 안에서 자연스럽게 관찰 |
| **M18** | HITL 웹 데모(승인·위임·자동승인) | [10.project/18.mcp_ops_assistant](../../../10.project/18.mcp_ops_assistant/) | 60m | 승인 게이트→서브에이전트 위임→자동승인, 4단계 라이브 시연 |

> 임팩트 큰 3순간: **M5**(LLM이 도구 자동 호출) · **M9**(자연어→SQL 조인) · **M8**(내가 붙인 서버를 클라가 호출). 시간 없으면 이 셋 사수.


============================================================
## 포맷 1 — 4시간 (예제 중심)
============================================================
**대상** MCP 처음 개발자, 그중에서도 **agent가 여러 MCP 도구를 라우팅·순차 실행하는 것**과
**HITL**을 반드시 체감시키고 싶은 경우
**구성** `M0 → M0.5a+b(llm-math 복습) → M1(stdio)+M3(transport) → M19+M20(mcp-math 로컬/원격) → M16(라우팅)+M17(실전 분기) → M18(HITL)`

**4대 섹션** (기획 원안 그대로 — 원안의 "4. LLM과 MCP 프로토콜의 상호작용"은 별도 블록이 아니라
**3번 데모(라우팅·순차·분기) 안에서 "LLM이 뭘 보고 어떤 도구를 고르고, 그게 어떻게 `call_tool`로
이어지는지"를 강사가 짚어주는 내레이션으로 흡수**했다 — 그 자체가 이미 LLM↔MCP 상호작용의 실물이라 별도 시간이 필요 없다.

| 섹션 | 시간대 | 포함 블록 |
|---|---|---|
| **1. MCP 프로토콜 개요**(agent·tool calling + MCP stdio) | 0:00–1:05 (65m) | 오리엔테이션 → llm-math 호출/직접제작 복습 → MCP stdio 첫 왕복 |
| **2. MCP 프로토콜을 통한 연결과 동작실행** | 1:05–2:00 (55m, 휴식 포함) | transport 비교 → mcp-math 로컬(stdio) 연동 → mcp-math 원격(HTTP) 연동 |
| **3. MCP tool 연결·Routing·순차실행·조건분기** (LLM↔MCP 상호작용 포함) | 2:00–3:15 (75m, 휴식 포함) | 여러 서버 라우팅 → 실전 순차·분기(멀티 컨시어지) — *진행 중 "지금 LLM이 왜 이 도구를 골랐는지" 짚어주기* |
| **4. Human-in-the-loop와 통합** | 3:15–4:00 (45m) | HITL 원리 → 라이브 데모 → 마무리 |

| 시간 | 내용 | 모듈/폴더 |
|------|------|-----------|
| _**1. MCP 프로토콜 개요**_ |||
| 0:00–0:10 | 오리엔테이션 — MCP=USB 비유, 오늘 만들 것 | M0 |
| 0:10–0:20 | **llm-math 호출** — 이미 만들어진 Calculator 도구를 `create_agent`로 부르기만 | M0.5a |
| 0:20–0:35 | **llm-math 직접 만들기** — `@tool`로 계산 도구 제작 → "근데 이 프로세스 밖에선 못 쓴다" | M0.5b |
| 0:35–1:05 | **MCP stdio 예제** — LLM 없이 손으로 `initialize→list_tools→call_tool` 첫 왕복 | M1 |
| _**2. MCP 프로토콜을 통한 연결과 동작실행**_ |||
| 1:05–1:20 | **MCP transport 예제** — 서버 코드로 stdio vs HTTP 비교(같은 도구, 전송만 다름) | M3 |
| 1:20–1:30 | ☕ 휴식 | |
| 1:30–1:45 | **mcp-math 로컬 연동** — 계산기를 MCP 서버로, stdio로 자식 프로세스 실행 | M19 |
| 1:45–2:00 | **mcp-math 원격 연동** — 같은 도구, `mcp.run()` 한 줄만 바꿔 HTTP로 접속 | M20 |
| _**3. MCP tool 연결·Routing·순차실행·조건분기**_ |||
| 2:00–2:35 | **여러 MCP 서버 라우팅** — math+utility 서버 동시 연결, 키워드→LLM 라우팅 고도화 | M16 |
| 2:35–2:45 | ☕ 휴식 | |
| 2:45–3:15 | **순차 실행과 조건 분기 (실전)** — 쇼핑몰+여행사 두 외부 서버를 챗봇이 오가며 처리. *"LLM이 뭘 보고 어떤 서버·도구를 골랐는지" 매 호출마다 짚어주기(= 원안 4번)* | M17 |
| _**4. Human-in-the-loop와 통합**_ |||
| 3:15–3:25 | HITL 원리 — 웹엔 `input()`이 없다: interrupt_before + checkpointer로 "저장소가 기다린다" | [8.mcp/4.langchain/6.human_in_loop](../../../8.mcp/4.langchain/6.human_in_loop/)(개념만) |
| 3:25–3:55 | **HITL 라이브 데모** — 승인 없음→승인 게이트→서브에이전트 위임→자동승인, 4단계를 브라우저로 시연 | M18(2~4단계) |
| 3:55–4:00 | 마무리 — 다음 단계 안내 | 7.guardrails · M10/M11/M12 |

> ⚠️ **시간 압박 시 트레이드오프**: 위 배치는 HITL 라이브 데모를 30분으로 압축했다(원래 M18 표준분량 60m).
> 4단계 전부를 보여주려면(승인 없음 1단계 포함) M16(라우팅, 35m)이나 M17(분기, 30m)에서 10~15분씩 덜어와야 한다.
> 반대로 라우팅/분기를 더 깊이 보고 싶다면 HITL을 "원리 설명 + `2.hitl_approve`/`4.auto_approve` 2단계만" 으로 줄인다.
>
> **시간이 남거나 "내 서버도 만들어보고 싶다" 요청이 나오면**: `2:00`(M16) 앞이나 `3:55` 마무리
> 자리에 15~20분 끼워 넣기 — [8.mcp/9.projects/4.mini_context7](../../../8.mcp/9.projects/4.mini_context7/)로
> "context7 같은 MCP 서버를 직접 만들고 `claude mcp add`로 VSCode/Claude Code에 등록"까지 라이브로 보여준다.
> API 키 없이 바로 돌아가서 시간 압박에 강하다.


============================================================
## 포맷 2 — 8시간 (원데이 집중)
============================================================
**대상** 팀 온보딩·부트캠프 · **구성** 오전=프로토콜·자동호출 / 오후=실전·인증

**오전 (약 3h40m + 휴식)**
| 시간 | 모듈 | 목표 |
|------|------|------|
| 0:00–0:20 | M0 | 개념 |
| 0:20–0:50 | M1 | 첫 왕복 |
| 0:50–1:30 | M2 | 3종 발견 · debug_proxy 정독 |
| 1:30–1:40 | ☕ | |
| 1:40–2:05 | M3 | 전송 stdio↔HTTP |
| 2:05–2:55 | M4 | 양방향 전부(sampling~roots) |
| 2:55–3:35 | M5 | LangChain 자동호출 |

**🍽 점심 (60m)**

**오후 (약 3h)**
| 시간 | 모듈 | 목표 |
|------|------|------|
| 4:35–5:20 | M8 | 클라이언트 등록 |
| 5:20–6:05 | M9 | DB 자연어 질의 |
| 6:05–6:15 | ☕ | |
| 6:15–7:15 | M10 | DB 인증 3모델 |
| 7:15–8:00 | M11 | 원격 배포·OAuth·TLS + 마무리 |
> M6/M7/M12/M16/M17/M18 은 관심사에 따라 M10↔교체 가능(포맷 1의 라우팅·HITL 블록을 오후에 끼워도 됨).


============================================================
## 포맷 3 — 16시간 (2일 집중 부트캠프)
============================================================
**대상** 사내 집중 교육 · 프로토콜부터 실전·보안·프로젝트까지 완주

**Day 1 — 기초·프로토콜·자동호출 (8h)**
| 블록 | 모듈 | 목표 |
|------|------|------|
| 오전1 | M0 · M1 · M2 | 개념 + 프로토콜 완주 |
| 오전2 | M3 · M4 | 전송 + 양방향 전부 |
| 🍽 점심 | | |
| 오후1 | M5 · M6 | LangChain + OpenAI 자동호출(두 스택 비교) |
| 오후2 | M7 | LangChain 심화(브릿지·안전성) |
| 마무리 | 복습·Q&A | Day2 예고 |

**Day 2 — 실전·클라이언트·보안·프로젝트 (8h)**
| 블록 | 모듈 | 목표 |
|------|------|------|
| 오전1 | M8 · M14 | 클라이언트 등록 + 운영(상태·인증) |
| 오전2 | M9 · M10 | DB 자연어 질의 + 인증 3모델 |
| 🍽 점심 | | |
| 오후1 | M11 · M12 | 원격 배포·OAuth·TLS + RAG를 MCP로 |
| 오후2 | M16 · M17 · M18 | 멀티서버 라우팅·순차분기 + HITL 웹 데모 |
| 마무리 | 발표·회고 | 각자 만든 MCP 서버 공유 |


============================================================
## 주제별 강조 트랙 (모듈 조합 가이드)
============================================================
길이와 무관하게 **관심사에 맞춰 모듈을 고르는** 방법.

| 트랙 | 골라 쓸 모듈 | 누구에게 |
|------|-------------|----------|
| **프로토콜 심화** | M1·M2·M3·**M4** (+debug_proxy·Inspector) | 플랫폼/프로토콜 엔지니어 |
| **에이전트 통합** | M1·M5·M6·**M7**·M12·M16·M17 | LLM/에이전트 개발자 |
| **DB 실무** | M1·M8·**M9**·**M10** (+원격 DB 인증) | 백엔드/데이터 |
| **보안·인증** | M4(roots)·**M10**·**M11**·M14·**M18**(HITL) | 보안/플랫폼 |
| **클라이언트 활용(쓰기)** | M8·**M14**·M9 | 서버를 만들기보다 쓰는 사람 |


============================================================
## 공통 준비물 & 강사 팁
============================================================
```bash
# 레포 최상위에 venv 하나 (하위 폴더별 X)
cd <레포 루트>
python -m venv .venv
.venv\Scripts\activate            # Windows (mac/linux: source .venv/bin/activate)
pip install -r 8.mcp/requirements.txt
node --version                    # 공식 서버용 Node 18+ (선택)
```
- **API 키**: `.env` 에 `OPENAI_API_KEY`(M5~M7·M12·M16), `ANTHROPIC_API_KEY`(Claude 연동).
- **DB 모듈(M9·M10)**: 각 폴더 `python init_db.py` 먼저.
- **원격/인증(M11)**: 서버 먼저 실행(터미널 2개). OAuth 로그인은 **대화형 터미널**.
- 자주 막히는 지점: `python`이 mcp 없는 인터프리터(venv 확인) · stdio 서버 stdout `print()` 금지 · DB `init_db.py` 먼저 · 원격 서버 선실행.
- **폴더 README를 슬라이드처럼** 써도 된다(실행법·관전 포인트 포함).

---
> 폴더별 상세=각 README · 학습 로드맵=[`8.mcp/README.md`](../../../8.mcp/README.md) · 클라이언트 운영=[`claude_code_mcp_guide.md`](../../../8.mcp/claude_code_mcp_guide.md)
