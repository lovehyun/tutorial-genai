# 3.elicitation — 도구 실행 중 사용자에게 되묻기

위험한 작업(삭제 등)이나 정보가 부족할 때, 서버는 도구 실행을 멈추고 **사용자에게 확인/추가 입력**을 요청한다.

```python
result = await ctx.elicit(message="정말 지울까요?", schema=ConfirmDelete)
# result.action: "accept" | "decline" | "cancel"
# result.data : accept 일 때만 채워짐(스키마대로 검증됨)
```

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
cd 8.mcp/1.common/4.advanced/3.elicitation
python client.py
```

## 관전 포인트
- **스키마는 원시 타입만**(`str/int/float/bool`) — 스펙 제약. 중첩 객체·리스트 불가.
- `action` **세 가지를 모두 처리**하라: `accept`(폼 제출) / `decline`(명시적 거절) / `cancel`(그냥 닫음). `accept` 여도 `confirm=false` 일 수 있다.
- 클라이언트가 `elicitation_callback` 을 안 주면 `Elicitation not supported` 에러.
- 실제 앱에서는 콜백 안을 `input()` 이나 GUI 다이얼로그로 바꾼다.

## 다음
- **[`../4.roots/`](../4.roots/)** — 클라이언트가 서버에 "접근 허용 경로" 를 알려주기
