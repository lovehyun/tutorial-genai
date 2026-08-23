# 8.grounding — 실시간 데이터로 답변 근거대기

모델이 답하기 전에 실시간 데이터를 조회해서 답의 근거로 삼습니다(내장 도구, 서버가 실행).

## 순서

| 파일 | 내용 |
|------|------|
| `1.google_search.py` | 구글 웹 검색 결과를 근거로 최신 정보 답변 |
| `2.google_maps.py` | **Google 전용 기능** — 구글 지도 데이터(평점·리뷰)를 근거로 장소 추천 |

## Google Maps 그라운딩 — 다른 벤더에 없는 기능

`2.google_maps.py`는 이 저장소 전체에서 **Google만 가진 유일한 기능**입니다. OpenAI·Anthropic
모두 웹 검색 도구는 있지만(`1.openai/2.sdk/13.response_web_search.py`,
`3.anthropic/2.tools/3.web_search.py`), 지도/장소 데이터에 특화된 그라운딩 도구는 없습니다.
위치 기반 추천(맛집·시설 안내 등)이 필요한 앱이라면 이 지점이 Gemini를 선택할 이유가 됩니다.

## 다른 벤더의 웹 검색 대응 기능

| 위치 | 비교 |
|------|------|
| [`../../1.openai/2.sdk/13.response_web_search.py`](../../1.openai/2.sdk/13.response_web_search.py) | OpenAI Responses API 내장 웹 검색 |
| [`../../3.anthropic/2.tools/3.web_search.py`](../../3.anthropic/2.tools/3.web_search.py) | Anthropic 서버 도구 웹 검색 |

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
