# OpenAI 스트리밍 예제

OpenAI API의 스트리밍(실시간 토큰 출력)을 **CLI → 웹(SSE) → 웹(단순화)** 순서로 익힙니다.
어느 파일이든 OpenAI 호출의 핵심은 동일하게 `stream=True` 한 줄입니다 — 달라지는 건
"받은 토큰 조각을 어디로 흘려보내느냐"뿐입니다.

## 예제 목록

| 폴더/파일 | 무엇을 보여주나 |
|-----------|------------------|
| `1.stream_cli.py` | 스트리밍 자체 — Flask도 SSE도 없이 콘솔에 토큰 그대로 출력 |
| `2.concept/` | 그 스트림을 **웹 브라우저**로 흘려보내는 정석 방법 (SSE 포맷) |
| `3.simple/` | 같은 걸 **포장을 벗기고** 더 간단하게 (SSE 없이 순수 텍스트) |

`2.concept/`, `3.simple/` 안에는 각각 웹앱 구조가 다른 파일 두 개가 있습니다 (내용은 동일, 프론트엔드
서빙 방식만 다름):

| 파일 (두 폴더 공통) | 웹앱 구조 | 프론트엔드 |
|------|-----------|-----------|
| `1.*_template.py` | 템플릿 엔진 (서버 사이드 렌더링) | `templates/index.html` (Jinja 처리) |
| `2.*_restapi.py` | REST API (정적 프론트 + API 백엔드) | `public/index.html` (정적 파일) |

## `2.concept` vs `3.simple` — 뭐가 다른가

**같은 점**: OpenAI SDK 호출(`stream=True`)도, 템플릿 엔진/REST API 구조 비교도 완전히 같습니다.
**다른 점**: 서버가 토큰을 클라이언트에 "어떤 포맷으로" 흘려보내느냐입니다.

| | `2.concept` (SSE 정석) | `3.simple` (포장 벗기기) |
|--|---|---|
| 서버가 보내는 것 | `data: {"content": "..."}\n\n` (SSE 포맷) | `content` 텍스트 그대로 |
| 종료 신호 | `data: [DONE]\n\n` | 없음 (연결이 끊기면 끝) |
| `mimetype` | `text/event-stream` | `text/plain` |
| 클라이언트 처리 | `split('\n')` → `data: ` 파싱 → `JSON.parse` | 받은 청크를 그대로 화면에 붙이기만 하면 끝 |

`2.concept`가 보여주는 SSE 포맷(`data:`/`event:`/`id:`)은 여러 종류의 이벤트를 구분하거나 브라우저의
`EventSource` API를 쓸 때 의미가 있는 정식 규격입니다 — 실제 OpenAI API 응답 스트림도 이 포맷입니다.
반면 지금처럼 텍스트 한 줄기만 받으면 되는 경우엔 그 포맷이 굳이 필요 없다는 걸 `3.simple`이 보여줍니다.
즉 `2.concept` → `3.simple`은 "기능이 추가되는" 관계가 아니라 "같은 결과를 더 적은 규약으로도 낼 수 있다"는
비교입니다.

## 실행

```bash
pip install openai python-dotenv    # 1.stream_cli.py
pip install flask                   # 2.concept/, 3.simple/ 추가로 필요

python 1.stream_cli.py                        # 콘솔에서 스트리밍 확인
python 2.concept/1.sse_stream_template.py     # 또는 2.concept/2.sse_stream_restapi.py
python 3.simple/1.stream_template.py          # 또는 3.simple/2.stream_restapi.py
# 웹 버전은 브라우저에서 http://localhost:5000 접속
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
