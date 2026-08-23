# 5.cancellation — 오래 걸리는 도구를 도중에 그만두게 하기

`2.progress_logging`이 "진행 상황을 보여주는" 채널이었다면, 이건 그 반대 방향 — **클라이언트가
서버에게 "그만 시켜"를 보내는** 채널이다. 사람이 답답해서 중간에 취소 버튼을 누르는 상황을 흉내낸다.

## 파일
| 파일 | 내용 |
|---|---|
| `server.py` | 1초마다 진행률을 흘리며 도는 `slow_task`(10초짜리) |
| `client.py` | 2.5초만 기다렸다가 취소 알림을 보내고, 서버가 실제로 멈추는 걸 확인 |

## 실행
```bash
pip install mcp
cd 5.mcp/1.basic/4.advanced/5.cancellation
python client.py
```

## 관전 포인트
- **`isError`가 아니라 프로토콜 레벨 에러**: 취소된 요청을 기다리면 `McpError("Request cancelled")`가
  발생한다 — `2.protocol_deep/9~10`에서 본 `isError=True`(정상 응답인데 내용이 실패)와는 다른 층이다.
- 서버 도구 안에서 `asyncio.CancelledError`를 잡아 정리 작업을 하고 **반드시 다시 raise** 해야
  취소가 완성된다 — 삼켜버리면(re-raise 안 하면) 서버가 계속 도는데 클라이언트만 포기한 상태가 된다.
- ⚠️ **이 SDK 버전엔 취소를 위한 공개 헬퍼가 없다** — `client.py`가 `session._request_id`(다음
  요청 ID, private 속성)를 직접 읽어 `CancelledNotification`을 수동으로 만든다. 실전에서는 SDK가
  공개 API를 제공하면 그쪽을 쓸 것 — 이 파일은 "취소가 프로토콜 레벨에서 어떻게 동작하는지"를
  보여주기 위한 것이다.

## 다음
- **[`../../2.protocol_deep/`](../../2.protocol_deep/)의 `9~10`번** — 취소가 아닌 "실행됐지만
  실패"(`isError`)와 비교해서 볼 것

## 설치
```bash
pip install mcp
```
