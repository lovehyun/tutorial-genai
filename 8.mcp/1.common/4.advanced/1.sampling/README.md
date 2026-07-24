# 1.sampling — 서버가 클라이언트의 LLM 에게 되묻기

지금까지 방향은 **클라이언트 → 서버**(도구 호출) 하나뿐이었다.
**Sampling** 은 그 반대다: 도구를 실행하던 **서버가 클라이언트에게 "이 프롬프트로 생성해줘"** 라고 되묻는다.

```
클라이언트 ── call_tool("summarize") ──▶ 서버
클라이언트 ◀── sampling/createMessage ── 서버   ← 도구 실행 도중, 역방향!
클라이언트 ── (자기 LLM 으로 생성) ─────▶ 서버
클라이언트 ◀── 도구 결과 ───────────────── 서버
```

## 왜 중요한가
- **서버는 LLM 을 소유하지 않는다.** API 키·모델은 클라이언트 쪽에 있다. 같은 서버가 GPT 클라이언트에 붙으면 GPT 로, Claude 에 붙으면 Claude 로 요약한다.
- "MCP 는 도구 호출만 하는 게 아니다" 를 보여주는 결정적 예제. MCP 의 **양방향성**.

## 파일
| 파일 | 무엇을 |
|---|---|
| `server.py` | `summarize` 도구가 `ctx.session.create_message(...)` 로 클라에게 생성 요청 |
| `client.py` | `ClientSession(..., sampling_callback=...)` 로 그 요청을 처리 (데모는 가짜 요약기) |

## 실행
```bash
pip install mcp
cd 8.mcp/1.common/4.advanced/1.sampling
python client.py        # server.py 를 자식 프로세스로 띄운다
```

## 관전 포인트
- 서버 도구가 sampling 을 쓰면, 클라이언트는 **반드시 `sampling_callback` 을 등록**해야 한다. 안 하면 `Sampling not supported` 에러(기본 콜백이 거부).
- `client.py` 의 콜백 안이 **진짜 LLM 을 호출할 자리**다. 데모는 '첫 문장만 뽑기' 로 대체 — 파일 하단 주석에 OpenAI 연결 예시.
- 콜백 시그니처(mcp 1.13): `async (context, params) -> CreateMessageResult | ErrorData`.

## 다음
- **[`../2.progress_logging/`](../2.progress_logging/)** — 오래 걸리는 도구의 진행률·로그 알림
