# 2.progress_logging — 오래 걸리는 도구의 진행률·로그

도구가 몇 초~몇 분 걸리면 클라이언트는 그동안 깜깜하다. MCP 는 **도구 실행 도중**
서버가 두 가지를 흘려보내게 한다 — 모두 `Context`(ctx) 객체로.

| 채널 | 서버 | 클라이언트 등록처 | 용도 |
|---|---|---|---|
| 진행률 | `ctx.report_progress(progress, total, message)` | `call_tool(..., progress_callback=...)` | 진행 막대 |
| 로그 | `ctx.info/debug/warning/error(...)` | `ClientSession(..., logging_callback=...)` | 로그 스트림 |

## 파일
| 파일 | 무엇을 |
|---|---|
| `server.py` | `batch_job` 이 처리하며 progress + info/warning 을 실시간 전송 |
| `client.py` | 두 콜백을 등록해 `[진행률 ..%]` / `[LOG:..]` 를 화면에 출력 |

## 실행
```bash
pip install mcp
cd 5.mcp/1.basic/4.advanced/2.progress_logging
python client.py
```

## 관전 포인트
- **`ctx: Context` 인자**를 도구에 추가하면 FastMCP 가 자동 주입한다 — 클라이언트가 넘기는 인자로는 **안 보인다**(도구 스키마에서 제외).
- 진행률과 로그는 **별개 채널**: 하나만 등록해도 되고, 등록 안 하면 그냥 버려진다(에러 아님).
- stdio 규칙 그대로 — 로그는 `print()` 가 아니라 `ctx.info()` 로. `print()` 는 JSON-RPC 채널(stdout)을 오염시킨다.

## 다음
- **[`../3.elicitation/`](../3.elicitation/)** — 도구 실행 중 사용자에게 되묻기(확인/추가입력)
