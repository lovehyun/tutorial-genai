# 실습 코드 — 4시간 포맷의 핸즈온

[`1.mcp_practice_4hr.md`](../1.mcp_practice_4hr.md)의 **4대 섹션**에 맞춰 파일 이름을 붙였다 —
`N` = 섹션 번호, `a/b/c...` = 그 섹션 안의 순서(주로 서버→클라이언트, 또는 단계 순).

instructor 전용 보너스 파일은 `{자리 알파벳}x` 로 표시한다 — student(todo)/answer 엔 없고,
정답이 정해진 TODO 순서에는 안 끼지만 "논리적으로 그 자리에 있는" 내용이라는 뜻이다. 예를 들어
`1cx`는 `1b` 다음(원래 `c` 자리)에 끼는 강사 전용 내용이라 `1cx`이고, 그 자리를 양보한 진짜 TODO
파일은 다음 알파벳(`1d`)으로 밀렸다. 끼어들 자리 없이 그냥 맨 뒤에 붙는 보너스(섹션 4의 두 파일)는
다음 비어 있는 알파벳에 `x`만 붙인다(`4cx`, `4dx`).

## 구성

| 폴더 | 용도 |
|---|---|
| [`1.instructor/`](1.instructor/) | 강사용 완성 코드 — 라이브 데모·정답 확인용. 각 파일 끝에 실제 실행 결과 첨부(웹 데모 제외) |
| [`2.student(todo)/`](2.student(todo)/) | 수강생 배포용 — 핵심 부분이 `TODO` 로 비어 있다 |
| [`3.student(answer)/`](3.student(answer)/) | 수강생 자가 채점용 — `TODO`가 있던 자리를 `DONE`으로 표시하고 채워둔 정답. 실행 결과는 안 붙어 있다(직접 돌려서 확인) |

## 섹션 1 — MCP 프로토콜 개요 (llm-math)

| 파일 | 내용 | 원본 |
|---|---|---|
| `1a.llm_math_call.py` | 빌트인 Calculator 도구를 `create_agent`로 부르기만 | [`2.langchain/8.agents/1.builtin_tools/1.1_llm_math.py`](../../../../2.langchain/8.agents/1.builtin_tools/1.1_llm_math.py) |
| `1b.llm_math_build.py` | `@tool`로 직접 도구 3개 제작, `bind_tools`로 "LLM이 뭘 고를지"만 확인(실행은 안 함) | [`2.custom_tools/2.2_at_tool_basic.py`](../../../../2.langchain/8.agents/2.custom_tools/2.2_at_tool_basic.py) |
| `1cx.multi_tool_call_manual.py`(**instructor 전용 보너스**, `1b`↔`1d` 사이) | 1b와 완전히 같은 도구 3개로 시작해서, `1d`가 `create_agent`로 자동화하는 5단계(판단→실행→결과추가→재호출→최종답변)를 손으로 그대로 구현 | [`4.internals/4.1_bind_tools.py`](../../../../2.langchain/8.agents/4.internals/4.1_bind_tools.py) (도구만 이 커리큘럼 것으로 교체, 로직은 거의 동일) |
| `1d.multi_tool_agent.py` | 1b의 도구 3개를 `create_agent`로 묶어 **실제로 실행**까지(ReAct 루프) | 원본에 정확히 일치하는 파일 없음 — [`2.1_first_agent.py`](../../../../2.langchain/8.agents/2.custom_tools/2.1_first_agent.py)(실행 패턴)와 [`2.3_at_tool_basic2_exec.py`](../../../../2.langchain/8.agents/2.custom_tools/2.3_at_tool_basic2_exec.py)(도구 3개)를 합성 |
| `1ex.ambiguous_tools.py`(**instructor 전용 보너스**, 순서를 안 타는 관찰용) | 뜻이 겹치는 도구를 일부러 두 개씩 만들어 같은 질문을 반복 호출 — LLM이 매번 같은 걸 고르는지, 오락가락하는지 실측 | 레포에 없음 — 이번 세션에서 직접 설계·실측 |

> **`1cx`가 왜 `1c`가 아니라 `1cx`인가**: 순서상으로는 `1b` 다음(=`c` 자리)이 맞다 — 이 파일은
> `1b`의 도구 3개를 **그대로** 가져와 실행 루프만 손으로 얹은 것뿐, 새로 설계한 게 아니다.
> 하지만 정답이 정해진 TODO가 아니라 **강사 전용으로 같이 안 짚고 넘어가도 되는 내용**이라
> `c`에 보너스 표시 `x`를 붙여 `1cx`로 이름 붙였고, 원래 `c`였던 `create_agent` 버전(지금의
> `1d`)은 다음 알파벳으로 밀렸다. `1cx`가 실은 `create_agent`가 내부에서 하는 일 그 자체이고,
> 이는 RAG와 구조가 같다는 통찰(검색이 "고정 단계"냐 "LLM이 고르는 도구 중 하나"냐의 차이 —
> 후자가 Agentic RAG)까지 파일 상단 docstring에 그대로 적어뒀다.
>
> `1ex`는 번호 순서를 일부러 벗어난 이름이다 — `a/b/c...`처럼 순차 진행에 끼는 파일이 아니라
> student(todo)/answer 엔 아예 없는 instructor 전용 보너스임을 **이름만 보고 바로 알 수 있게** 했다.
> "정답이 있는 TODO"가 아니라 **관찰 자체가 목적**이라(temperature=1.0, 실행마다 결과가 달라짐)
> 빈칸 채우기 구조에 안 맞기도 하다. 실측 결과: 뜻이 살짝 다른 쌍은 실행마다 4:4로 갈리기도
> 하고 한쪽이 8:0으로 싹쓸이하기도 했다 — 순서를 바꿔도 "먼저 나열된 쪽이 이긴다"는 단순 법칙이
> 깨지는 경우도 나왔다(자세한 수치는 파일 하단 주석 참고). 결론: LLM 도구 선택은 완전한 동전 던지기도
> 완전한 결정도 아니다 — "왜 이 도구가 불렸는지" 100% 예측 못 한다는 것 자체가 실무 교훈이다.

## 섹션 2 — MCP 프로토콜을 통한 연결과 동작실행 (mcp-math)

| 파일 | 내용 | 원본 |
|---|---|---|
| `2a.mcp_math_local_server.py` / `2b.mcp_math_local_client.py` | mcp-math 로컬 연동(stdio) | [`8.mcp/2.openai/2.multi_tools/math_server.py`](../../../../8.mcp/2.openai/2.multi_tools/math_server.py) + `1.math_client.py` |
| `2bx.mcp_math_local_client_debug.py`(**instructor 전용 보너스**) + `debug_proxy.py`(비실습, 지원용 — 세 폴더 모두 원본 그대로) | 2a 서버는 그대로 두고 클라이언트만 `debug_proxy.py`를 경유하도록 바꿔서, `call_tool` 한 줄이 실제로는 `initialize → list_tools → call_tool` JSON-RPC 왕복이라는 걸 로그로 직접 확인 | [`8.mcp/1.basic/2.protocol_deep/2.simple_client.py`](../../../../8.mcp/1.basic/2.protocol_deep/2.simple_client.py)(프록시 경유 방식) + [`debug_proxy.py`](../../../../8.mcp/1.basic/2.protocol_deep/debug_proxy.py) |
| `2c.mcp_math_remote_server.py` / `2d.mcp_math_remote_client.py` | mcp-math 원격 연동(HTTP) — `mcp.run()` 한 줄만 다름 | [`4.langchain/5.remote_http/1.server_simple.py`](../../../../8.mcp/4.langchain/5.remote_http/1.server_simple.py) + `2.client_agent.py` |

> **`2bx`가 왜 서버(2a)는 안 건드리고 클라이언트만 바꾸나**: debug_proxy는 클라↔서버 "사이"에
> 끼는 중계자다 — 서버 코드는 한 글자도 안 바뀐다, 클라이언트가 접속 대상을 `2a` 대신
> `debug_proxy.py 2a`로 바꿀 뿐이다(`2b`와 다른 부분은 `StdioServerParameters`의 `args` 한 줄).
> `debug_proxy.py`는 이 실습의 교재 내용이 아니라 그 자체가 도구라 알파벳을 안 받았다 —
> `3a`/`3b`처럼 "실습 대상은 아니지만 실행에 필요한" 지원 파일이다. 다만 이 유틸은 학생도 직접
> 만져볼 가치가 있어서 `2bx`(강사 전용)와 달리 **`debug_proxy.py` 자체는 세 폴더 모두에 원본
> 그대로 들어 있다** — 시간이 남으면 학생도 자기 `2b`를 복사해 `args`만 바꿔 똑같이 해볼 수 있다.

## 섹션 3 — Routing·순차실행·조건분기 (심화)

| 파일 | 내용 | 원본 |
|---|---|---|
| `3a.math_server.py` / `3b.utility_server.py`(비실습, 지원용) | 도메인이 다른 두 서버(계산 vs 시간·날씨) | [`8.mcp/2.openai/2.multi_tools/`](../../../../8.mcp/2.openai/2.multi_tools/) `math_server.py` + `utility_server.py` |
| `3c.routing_manual.py` | **라우팅 1단계**: 키워드 규칙(`find_tool`/`extract_params`)으로 수동 선택, LLM 없음 | [`3.smart_client_manual.py`](../../../../8.mcp/2.openai/2.multi_tools/3.smart_client_manual.py) |
| `3d.routing_llm_gpt.py` | **라우팅 2단계**: GPT function calling이 질의 보고 자동 선택 | [`4.smart_client_gpt.py`](../../../../8.mcp/2.openai/2.multi_tools/4.smart_client_gpt.py) |

`3a`/`3b`는 실습 대상이 아니다(서버는 클라이언트가 stdio로 자동 실행) — 실행에 필요해서 넣었다.

> **왜 3c/3d가 raw OpenAI SDK인가**: 나머지 전부 LangChain `create_agent`로 통일했지만, 이 둘은
> "규칙 기반 → LLM 라우팅"으로 넘어가는 순간 자체가 목적이라 **LLM이 도구 스키마만 보고 뭘 부를지
> 스스로 정하는 raw 메커니즘**을 한 겹 벗겨서 보여준다. LangChain `create_agent`도 내부적으론 같은 일을
> 하지만 감싸서 안 보인다. 같은 라우팅을 LangChain으로 다시 보고 싶으면 —
> [`4.langchain/1.quickstart/4.multi_server.py`](../../../../8.mcp/4.langchain/1.quickstart/4.multi_server.py) (포맷 1의 "시간 남으면" 보너스).

## 섹션 4 — Human-in-the-loop

| 파일 | 내용 | 원본 |
|---|---|---|
| `4a.hitl_approval_server.py`(비실습, 지원용) / `4b.hitl_approval_client.py` | HITL 승인 게이트(CLI) — `checkpointer`+`interrupt_before` 두 인자가 핵심 | [`8.mcp/4.langchain/6.human_in_loop/server.py`](../../../../8.mcp/4.langchain/6.human_in_loop/server.py) + `1.approval_gate.py` |
| `4cx.hitl_auto_approve.py`(**instructor 전용 보너스**) | "항상 허용"을 한 번 고르면 같은 도구는 다음부턴 안 묻는다(`AUTO_APPROVED` 집합) — 4b를 확장 | 레포에 CLI 형태로는 없음 — `18.mcp_ops_assistant/4.auto_approve`의 아이디어를 이번 세션에서 CLI로 재구성 |
| [`4dx.hitl_web_demo/`](1.instructor/4dx.hitl_web_demo/)(**instructor 전용 보너스**) | 같은 HITL을 웹 화면(승인 카드)으로 — CLI `input()` 대신 승인 대기 상태를 저장소에 남기고 재개하는 구조 | [`10.project/18.mcp_ops_assistant/2.hitl_approve/`](../../../../10.project/18.mcp_ops_assistant/2.hitl_approve/) |

`4cx`/`4dx` 둘 다 `2.student(todo)`·`3.student(answer)`에는 없다 — 4시간 안에 다 못 다룰 수 있어
**강사가 시간 남으면 보여주는 용도**로만 instructor 폴더에 넣었다. 둘 다 `4a`/`4b` 다음에
끼어드는 게 아니라 그 뒤에 붙는 보너스라, 다음 비어 있는 알파벳(`c`, `d`)에 각각 `x`를 붙였다.

## TODO 채우는 순서 (`2.student(todo)/`)

각 파일에서 완성된 예시 하나를 먼저 보여주고, **같은 패턴으로 채워야 할 TODO 하나**를 남겨뒀다 —
새로 배우는 게 아니라 "방금 본 패턴을 한 번 더 반복"하는 구조다.

1. **`1a.llm_math_call.py`** — `tools` / `agent` / `result` 3줄
2. **`1b.llm_math_build.py`** — `calculate_tip` 함수 하나 + `lookup_user` 함수 하나(`@tool` + 구현)
3. **`1d.multi_tool_agent.py`** — `agent = create_agent(...)` + `agent.invoke(...)` 두 줄
4. **`2a/2b`** — `add` 도구 정의(서버) + `add` 호출(클라이언트)
5. **`2c/2d`** — `mcp.run(transport=...)` 한 줄(서버) + 접속 설정 딕셔너리(클라이언트)
6. **`3c.routing_manual.py`** — "날씨" 라우팅 규칙(`find_tool`) + 파라미터 추출(`extract_params`)
7. **`3d.routing_llm_gpt.py`** — MCP 도구→OpenAI 함수 스키마 변환 + GPT가 고른 도구를 올바른 서버로 실행
8. **`4b.hitl_approval_client.py`** — `create_agent`에 `checkpointer`·`interrupt_before` 두 인자

`2c/2d`가 이 실습의 핵심이다 — **로컬↔원격을 가르는 코드가 정말 한 줄/한 딕셔너리뿐**이라는 걸
손으로 직접 확인하게 되어 있다. `3c`→`3d`는 **같은 라우팅을 규칙 기반과 LLM 기반으로 각각 짜보면서
"규칙은 왜 번거롭고 LLM은 왜 편한가"**를 비교하는 게 목적이다. `4b`는 **HITL 원리가 코드 두 줄임을**
직접 확인하는 게 목적이다.

## 실행

```bash
cd exercise/2.student(todo)          # 또는 1.instructor, 3.student(answer)
pip install mcp langchain langchain-openai langchain-community langchain-mcp-adapters langgraph openai python-dotenv numexpr
# .env 에 OPENAI_API_KEY 필요 (이 폴더에 직접 두거나, 레포 루트 .env 를 상속받게 실행 위치 조정)

python 1a.llm_math_call.py
python 1b.llm_math_build.py
python 1d.multi_tool_agent.py
python 2b.mcp_math_local_client.py       # 서버(2a)는 클라이언트가 stdio 로 자동 실행

# 2c/2d는 서버를 먼저 띄워야 한다 (터미널 2개)
python 2c.mcp_math_remote_server.py      # 터미널 1
python 2d.mcp_math_remote_client.py      # 터미널 2

python 3c.routing_manual.py              # 심화 1단계 — 3a/3b 서버 모두 stdio 로 자동 실행
python 3d.routing_llm_gpt.py             # 심화 2단계 — 같은 서버, raw OpenAI SDK 로 GPT 가 라우팅
python 4b.hitl_approval_client.py        # 심화 — 실행 중 y/n 입력 필요 (list_files, delete_file 두 번 멈춤)

# instructor 전용 보너스 (student 폴더엔 없음)
python 1cx.multi_tool_call_manual.py     # (1.instructor 안에서) — create_agent 내부를 손으로 재현
python 1ex.ambiguous_tools.py            # (1.instructor 안에서) — 실행마다 결과가 달라짐
python 2bx.mcp_math_local_client_debug.py  # (1.instructor 안에서) — debug_proxy 경유, JSON-RPC 로그 확인
python 4cx.hitl_auto_approve.py          # (1.instructor 안에서) — 첫 승인 프롬프트에서 'a' 입력해보기

cd 1.instructor/4dx.hitl_web_demo
pip install flask langgraph-checkpoint-sqlite
python app.py                            # → http://localhost:5082
```

`2b`는 `SERVER_FILE = "2a.mcp_math_local_server.py"`로, `2bx`도 같은 `2a`를 재사용하고, `3c`/`3d`는
`SERVERS = ["3a.math_server.py", "3b.utility_server.py"]`로, `4b`/`4cx`는
`SERVER = ".../4a.hitl_approval_server.py"`로 같은 폴더의 서버 파일명을 하드코딩하고 있다 —
파일을 옮기거나 이름을 바꾸면 이 값도 같이 바꿔야 한다.
