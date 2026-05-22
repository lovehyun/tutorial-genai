# OpenAI 스트리밍 예제

OpenAI API의 스트리밍(실시간 토큰 출력)을 **웹앱 구조 두 가지**로 구현해 비교합니다.
OpenAI 호출은 두 파일 모두 SDK를 쓰며, 차이는 '프론트엔드를 어떻게 서빙하느냐'뿐입니다.

## 예제 목록

| 파일 | 웹앱 구조 | 프론트엔드 |
|------|-----------|-----------|
| `1.sse_stream_template.py` | 템플릿 엔진 (서버 사이드 렌더링) | `templates/index.html` (Jinja 처리) |
| `2.sse_stream_restapi.py` | REST API (정적 프론트 + API 백엔드) | `public/index.html` (정적 파일) |

`/stream` SSE 엔드포인트와 OpenAI SDK 호출 코드는 두 파일이 완전히 동일합니다.
다른 것은 메인 페이지(`/`)를 내려주는 방식뿐입니다.

## 두 구조의 차이

| | 템플릿 엔진 방식 | REST API 방식 |
|--|-----------------|---------------|
| HTML 처리 | 서버가 Jinja로 가공 (`render_template`) | 가공 없이 그대로 전달 (`send_from_directory`) |
| 서버 데이터 주입 | `{{ 변수 }}`로 가능 | 불가 (필요하면 API로 받음) |
| 프론트/백 결합도 | 한 몸 | 분리 — 프론트를 따로 호스팅 가능 |
| HTML 위치 | `templates/` | `public/` |

## 핵심 개념

- **Server-Sent Events (SSE)**: 서버 → 클라이언트 단방향 실시간 데이터 전송
- **stream=True**: OpenAI가 응답을 토큰 단위로 흘려보냄
- **타이핑 효과**: 토큰이 도착할 때마다 즉시 화면에 표시

## 설치 및 실행

```bash
pip install flask openai python-dotenv
python 1.sse_stream_template.py   # 또는 2.sse_stream_restapi.py
# 브라우저에서 http://localhost:5000 접속
```

API 키는 상위 폴더의 `.env`(`../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
