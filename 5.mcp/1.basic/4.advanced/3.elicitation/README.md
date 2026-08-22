# 3.elicitation — 도구 실행 중 사용자에게 되묻기

> **elicit**(동사) = (정보·응답을) **끌어내다, 이끌어내다** (라틴어 *ex-*'밖으로' + *lacere*'꾀다').
> **elicitation** = 이끌어냄·정보 도출. MCP 에선 **서버가 사용자에게서 필요한 결정/정보를 끌어내는 것** = 되묻기.

위험한 작업(삭제 등)이나 정보가 부족할 때, 서버는 도구 실행을 멈추고 **사용자에게 확인/추가 입력**을 요청한다.

```python
result = await ctx.elicit(message="정말 지울까요?", schema=ConfirmDelete)
# result.action: "accept" | "decline" | "cancel"
# result.data : accept 일 때만 채워짐(스키마대로 검증됨)
```

## 어떻게 이루어지나 (단계별)
```
도구 실행 중 ──────────────────────────────────
① 서버: await ctx.elicit(message=..., schema=ConfirmDelete)
        │  (도구가 '멈춤' — 사용자 답을 기다림)
        ▼  elicitation/create 요청 (서버→클라, 역방향 JSON-RPC)
② 클라: elicitation_callback 발동 → 사용자에게 message+폼 제시, 입력 수집(input()/GUI)
        ▼  ElicitResult(action, content) 반환
③ 서버: action 확인 + content 를 schema 로 검증 → 도구 로직 계속
```
핵심: 도구가 `await` 로 **멈춰서 사람의 답을 기다린다** = human-in-the-loop(사람 개입).

## 뭐가 특색인가
- **서버가 자기 UI 없이 사람에게 묻는다** — UI(다이얼로그/프롬프트)는 **클라이언트 소유**. 서버는 "이 메시지+폼으로 물어봐"만 보냄 → 터미널/IDE/웹 어느 클라든 각자 방식으로 표시.
- **런타임 조건부 질문** — 실행 도중 상태를 보고 물을 수 있다. 예) *"이 파일 2GB인데 그래도 지울래?"* (실행 전엔 크기를 몰라 못 묻던 것).
- **sampling 과 대비** — sampling=클라의 **LLM(기계)**, elicit=**사용자(사람)**.
- **최신 기능** — 2025-06-18 스펙에서 추가(sampling·roots 는 초기부터).

**sampling 과의 차이** — 방향은 둘 다 서버→클라지만 상대가 다르다:
- `sampling` = 서버가 **클라이언트의 LLM(기계)** 에게 되물음
- `elicit` = 서버가 **사용자(사람)** 에게 되물음

## 파일
| 파일 | 무엇을 |
|---|---|
| `server.py` | `delete_file` 이 삭제 전에 `ctx.elicit(...)` 로 확인 폼을 띄움 |
| `client.py` | `ClientSession(..., elicitation_callback=...)` 로 응답(데모는 자동: 1번째 승인, 2번째 취소) |

## 실행
```bash
pip install mcp
cd 8.mcp/1.basic/4.advanced/3.elicitation
python client.py
```

## 관전 포인트
- **스키마는 원시 타입만**(`str/int/float/bool`) — 스펙 제약. 중첩 객체·리스트 불가.
- `action` **세 가지를 모두 처리**하라: `accept`(폼 제출) / `decline`(명시적 거절) / `cancel`(그냥 닫음). `accept` 여도 `confirm=false` 일 수 있다.
- 클라이언트가 `elicitation_callback` 을 안 주면 `Elicitation not supported` 에러.
- 실제 앱에서는 콜백 안을 `input()` 이나 GUI 다이얼로그로 바꾼다.

## 다음
- **[`../4.roots/`](../4.roots/)** — 클라이언트가 서버에 "접근 허용 경로" 를 알려주기
