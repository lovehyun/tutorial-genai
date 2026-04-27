# 챗봇 UI (Flask 웹 챗봇)

OpenAI API와 Flask를 사용한 웹 기반 챗봇의 기본 구현입니다.

## 핵심 개념

- Flask 웹 서버로 채팅 인터페이스 제공
- REST API 직접 호출 vs OpenAI SDK 사용 비교
- 프론트엔드(HTML/JS)와 백엔드(Python) 연동

## 예제 목록

| 파일 | 설명 |
|------|------|
| `app_restapi.py` | requests로 OpenAI API 직접 호출 |
| `app2_openailib.py` | OpenAI SDK 사용 버전 |

## 실행

```bash
pip install flask openai python-dotenv
python app2_openailib.py
# 브라우저에서 http://localhost:5000
```
