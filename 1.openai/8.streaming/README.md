# OpenAI 스트리밍 예제

OpenAI API의 스트리밍 기능을 활용한 실시간 응답 예제입니다.

## 예제 목록

| 파일 | 설명 |
|------|------|
| `1.sse_stream.py` | Flask SSE 기반 실시간 스트리밍 (ChatGPT 스타일 UI) |

## 핵심 개념

- **Server-Sent Events (SSE)**: 서버에서 클라이언트로 단방향 실시간 데이터 전송
- **stream=True**: OpenAI API에서 토큰 단위로 응답을 스트리밍
- **타이핑 효과**: 토큰이 생성될 때마다 즉시 화면에 표시

## 설치 및 실행

```bash
pip install openai flask
python 1.sse_stream.py
# 브라우저에서 http://localhost:5000 접속
```
