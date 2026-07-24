# 1.common/4.advanced — MCP 심화: Context 와 양방향

`1.intro ~ 3.transports` 까지는 방향이 **클라이언트 → 서버(도구 호출)** 하나뿐이었다.
여기서는 MCP 의 **양방향** 기능과 **`Context`(ctx) 객체**를 다룬다 —
서버가 실행 도중 클라이언트에게 되묻거나(모델·사람), 클라이언트가 서버에 컨텍스트를 준다.

> 전부 **provider/framework 중립**(순수 MCP). LLM 없이 흐름만으로 이해할 수 있게 콜백은 '가짜' 로 채웠다.

## 4가지 패턴

| 폴더 | 패턴 | 방향 | 서버 API | 클라이언트 등록 |
|---|---|---|---|---|
| [`1.sampling/`](1.sampling/) | 서버가 **클라의 LLM** 에게 생성 요청 | 서버→클라(기계) | `ctx.session.create_message` | `sampling_callback` |
| [`2.progress_logging/`](2.progress_logging/) | 오래 걸리는 도구의 **진행률·로그** | 서버→클라(알림) | `ctx.report_progress` / `ctx.info` | `progress_callback` / `logging_callback` |
| [`3.elicitation/`](3.elicitation/) | 서버가 **사용자** 에게 확인·입력 요청 | 서버→클라(사람) | `ctx.elicit` | `elicitation_callback` |
| [`4.roots/`](4.roots/) | 클라가 서버에 **허용 경로** 통지 | 서버→클라(설정) | `ctx.session.list_roots` | `list_roots_callback` |

### 한눈에 보는 공통 구조
- 서버 도구에 **`ctx: Context`** 인자를 추가 → FastMCP 가 자동 주입(클라 인자엔 안 보임).
- 클라이언트는 **`ClientSession(read, write, <xxx>_callback=...)`** 로 콜백을 등록.
- 콜백을 **안 주면** 해당 요청은 `... not supported` 로 거부되거나(progress/log 는) 조용히 버려진다.

## 학습 순서
```
1.sampling         "MCP 는 도구 호출만 하는 게 아니다" — 양방향의 핵심     ★★★
   ▼
2.progress_logging 실전 필수 — 긴 작업의 진행률/로그                       ★★★
   ▼
3.elicitation      사람에게 되묻기(확인/입력)                             ★★
   ▼
4.roots            클라가 서버에 접근 범위를 통지                         ★★
```

## 실행 (각 폴더 공통)
```bash
pip install mcp
cd 8.mcp/1.common/4.advanced/<폴더>
python client.py        # 각 폴더의 server.py 를 자식 프로세스로 띄운다
```

## 다음 단계
- 원격 서버 **인증(OAuth2/Bearer)**: [`../../9.projects/2.remote/2.oauth/`](../../9.projects/2.remote/2.oauth/)
- LLM 자동 호출로 돌아가기: [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)

> 참고: 이 콜백들은 MCP Inspector(`mcp dev server.py`)에서도 눌러볼 수 있다(Node 18+).
