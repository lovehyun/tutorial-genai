# 1.basic/4.advanced — MCP 심화: Context 와 양방향

`1.intro ~ 3.transports_http` 까지는 방향이 **클라이언트 → 서버(도구 호출)** 하나뿐이었다.
여기서는 MCP 의 **양방향** 기능과 **`Context`(ctx) 객체**를 다룬다 —
서버가 실행 도중 클라이언트에게 되묻거나(모델·사람), 클라이언트가 서버에 컨텍스트를 준다.

> 전부 **provider/framework 중립**(순수 MCP). LLM 없이 흐름만으로 이해할 수 있게 콜백은 '가짜' 로 채웠다.

## 5가지 패턴

| 폴더 | 패턴 | 방향 | 서버 API | 클라이언트 등록 |
|---|---|---|---|---|
| [`1.sampling/`](1.sampling/) | 서버가 **클라의 LLM** 에게 생성 요청 | 서버→클라(기계) | `ctx.session.create_message` | `sampling_callback` |
| [`2.progress_logging/`](2.progress_logging/) | 오래 걸리는 도구의 **진행률·로그** | 서버→클라(알림) | `ctx.report_progress` / `ctx.info` | `progress_callback` / `logging_callback` |
| [`3.elicitation/`](3.elicitation/) | 서버가 **사용자** 에게 확인·입력 요청 | 서버→클라(사람) | `ctx.elicit` | `elicitation_callback` |
| [`4.roots/`](4.roots/) | 클라가 서버에 **허용 경로** 통지 | 서버→클라(설정) | `ctx.session.list_roots` | `list_roots_callback` |
| [`5.cancellation/`](5.cancellation/) | 클라가 **실행 중인 도구를 중단** | 클라→서버(중단 요청) | `asyncio.CancelledError` 처리 | `CancelledNotification` 전송 |

### 한눈에 보는 공통 구조
- 서버 도구에 **`ctx: Context`** 인자를 추가 → FastMCP 가 자동 주입(클라 인자엔 안 보임).
- 클라이언트는 **`ClientSession(read, write, <xxx>_callback=...)`** 로 콜백을 등록.
- 콜백을 **안 주면** 해당 요청은 `... not supported` 로 거부되거나(progress/log 는) 조용히 버려진다.

## 어떻게 서버가 "먼저" 되물을 수 있나 — 지속 세션 + 양방향

> "클라 요청도 없는데 서버가 어떻게 물어봐?" 의 답: MCP 는 **요청 하나 보내고 끊는 REST 가 아니다.**
> `initialize` 로 **세션을 맺으면 그 연결이 끝까지 열린 채** 유지되고, 그 위로 **JSON-RPC 가 양방향**으로 흐른다.
> 클라만 요청하는 게 아니라 **서버도 요청을 보낼 수 있다**(각 메시지의 `id` 로 요청↔응답을 매칭).

사실 "생판 아무것도 없는데 서버가 먼저"가 아니라, **클라가 부른 도구를 처리하는 '도중'** 같은 열린 연결로 되쏘는 것:

```
① 클라 ── tools/call("delete_file") ──▶ 서버      (클라가 먼저 요청)
                                          │ 도구 실행 시작
② 클라 ◀── elicitation/create ─────────── 서버      ← 도중에 서버가 '되물음'
                                          │ 도구는 await 로 멈춰 답을 기다림
③ 클라 ── ElicitResult(accept) ────────▶ 서버
                                          │ 도구 로직 계속
④ 클라 ◀── tools/call 응답 ─────────────── 서버      (그제서야 원래 응답)
```
①의 응답(④)이 아직 안 나간 사이에, **같은 연결로** 서버가 새 요청(②)을 끼워넣는다.

**물리적으로 가능한 이유 = 전송이 지속 양방향 스트림:**
- **stdio**: 클라가 서버를 자식 프로세스로 띄우고 **stdin/stdout 파이프가 세션 내내 열림.** 클라는 서버 stdout 을 **비동기 read 루프**로 계속 듣는다 → 도구 응답을 기다리는 중에도 서버의 `elicitation/create` 를 집어 콜백으로 넘긴다. (그래서 클라가 **async/이벤트 루프**여야 한다 — [`../1.intro/4.hello_client.py`](../1.intro/4.hello_client.py) 주석의 그 이유.)
- **HTTP(streamable)**: `tools/call` POST 가 **SSE 스트림을 열어둔 채**, 서버가 최종 응답 전에 그 스트림으로 추가 메시지(요청 포함)를 push.

**누가 뭘 할 수 있나는 `initialize` 에서 미리 합의**: capability 교환 시 클라가 *"나 elicitation/sampling/roots 지원"* 을 선언해야 서버가 쓴다(안 하면 `... not supported`).

**요청(request) vs 알림(notification)** — 둘 다 서버→클라지만:
| | 예제 | 응답 필요? | "도중"인가 |
|---|---|---|---|
| **요청** | sampling · elicitation · roots | ✅ 클라가 답해야 함 | 도구 처리 도중(nested) |
| **알림** | progress · logging | ❌ 일방 push | 도구 처리 도중 |
| (참고) 독립 알림 | `notifications/*/list_changed` 등 | ❌ | **요청 없이도 아무 때나** push 가능 |

## 학습 순서
```
1.sampling         "MCP 는 도구 호출만 하는 게 아니다" — 양방향의 핵심     ★★★
   ▼
2.progress_logging 실전 필수 — 긴 작업의 진행률/로그                       ★★★
   ▼
3.elicitation      사람에게 되묻기(확인/입력)                             ★★
   ▼
4.roots            클라가 서버에 접근 범위를 통지                         ★★
   ▼
5.cancellation     클라가 실행 중인 도구를 중단 — progress_logging 의 반대 방향  ★★
```

## 실행 (각 폴더 공통)
```bash
pip install mcp
cd 5.mcp/1.basic/4.advanced/<폴더>
python client.py        # 각 폴더의 server.py 를 자식 프로세스로 띄운다
```

## 다음 단계
- 원격 서버 **인증(OAuth2/Bearer)**: [`../../10.projects/2.remote/2.oauth/`](../../10.projects/2.remote/2.oauth/)
- LLM 자동 호출로 돌아가기: [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)

> 참고: 이 콜백들은 MCP Inspector(`mcp dev server.py`)에서도 눌러볼 수 있다(Node 18+).
