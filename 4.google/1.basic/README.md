# 1.basic — Gemini API 기초

`google-genai` SDK로 가장 단순한 호출부터 스트리밍까지 익힙니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.intro.py` | 텍스트 생성 — 가장 단순한 호출 |
| `2.chat.py` | 멀티턴 대화 — `client.chats.create()` |
| `3.params.py` | 파라미터 제어 — temperature, top_p, top_k |
| `4.stream.py` | 스트리밍 응답 |

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`

## 참고

구조화 출력은 [`../2.structured_output/`](../2.structured_output/)로 분리했습니다 — 이 폴더는
순수 기초만 다룹니다.
