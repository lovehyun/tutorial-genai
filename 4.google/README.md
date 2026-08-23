# 4. Google Gemini

Google Gemini API를 활용한 예제를 기초부터 단계별로 학습합니다. 각 폴더는 **하나의 주제**를
다룹니다(1.openai, 2.langchain, 3.anthropic과 같은 조직 원리).

## 학습 순서

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.basic/` | API 기초 | 텍스트 생성 → 멀티턴 → 파라미터 → 스트리밍 |
| `2.structured_output/` | 구조화 출력 | Pydantic 스키마로 JSON 강제 |
| `3.tools/` | 도구 호출 | 함수 호출 + 코드 실행(내장 도구) |
| `4.vision/` | 이미지 입력 | 이미지 분석(생성 아님) |
| `5.image_generation/` | 이미지 생성 | 텍스트→이미지 + 대화형 편집 (⚠️ Imagen 종료, API 변경됨) |
| `6.video_understanding/` | **비디오 이해** | 다른 벤더에 없는 기능 — 영상을 시간 흐름째로 이해 |
| `7.video_generation/` | 동영상 생성 | 텍스트→영상, Veo 3.1 + 비동기 폴링 (⚠️ 초당 $0.40) |
| `8.grounding/` | 실시간 그라운딩 | 구글 검색 + **구글 지도(Google 전용)** |
| `9.embeddings/` | 임베딩 | 텍스트 → 벡터 → 시맨틱 서치, RAG의 첫 단계 |
| `10.langchain/` | LangChain 연동 | `ChatGoogleGenerativeAI`로 프롬프트/체인/구조화 출력 |

## 🌟 Google만의 특장점

이 저장소의 다른 벤더 폴더(`1.openai`, `3.anthropic`)에는 없는, Google Gemini만의 기능입니다.

| 기능 | 위치 | 왜 특별한가 |
|------|------|-------------|
| **비디오 이해** | `6.video_understanding/` | 프레임 샘플링이 아니라 영상을 시간 흐름·오디오까지 통째로 이해. OpenAI·Anthropic은 이미지/PDF까지만 지원 |
| **Google Maps 그라운딩** | `8.grounding/2.google_maps.py` | 실제 지도 데이터(평점·리뷰)로 장소를 추천 — 이 저장소에서 유일하게 Google만 가진 도구 |
| **대화형 이미지 편집** | `5.image_generation/3.conversational_editing.py` | 생성한 이미지를 대화하듯 계속 수정(나머지 요소는 유지) |

`7.video_generation/`(Veo 3.1 동영상 생성)은 OpenAI에도 Sora가 있어 Google 독점은 아니지만,
이 저장소에는 아직 OpenAI 쪽 동영상 생성 예제가 없어 현재로선 Google에서만 다룹니다.

## 사전 준비

```bash
pip install google-genai langchain-google-genai python-dotenv Pillow numpy
```

`.env` 파일에 Google API 키를 설정하세요:
```
GOOGLE_API_KEY=...
```

## ⚠️ 2026년에 바뀐 것 — Imagen 서비스 종료

`5.image_generation/`은 원래 Imagen 3 전용 모델을 썼는데, **2026-08-17부로 Imagen 계열이
전부 서비스 종료**됐습니다. 지금은 일반 Gemini 모델(`gemini-2.5-flash-image`)이 이미지 생성까지
겸합니다. 호출 방식도 `client.models.generate_images()` → `client.interactions.create()`로
바뀌었습니다 — 자세한 건 [`5.image_generation/README.md`](5.image_generation/README.md) 참고.

## 다른 벤더와 비교

| 개념 | OpenAI | Anthropic | Google |
|------|--------|-----------|--------|
| 구조화 출력 | `1.openai/6.structured_output/` | `3.anthropic/3.structured_output/` | `2.structured_output/` |
| 함수 호출 | `1.openai/7.function_calling/` | `3.anthropic/2.tools/1.tool_use.py` | `3.tools/1.function_calling.py` |
| 코드 실행(내장 도구) | — | `3.anthropic/2.tools/4.code_execution.py` | `3.tools/2.code_execution.py` |
| 웹 검색(내장 도구) | `1.openai/2.sdk/13.response_web_search.py` | `3.anthropic/2.tools/3.web_search.py` | `8.grounding/1.google_search.py` |
| 지도 그라운딩 | — | — | `8.grounding/2.google_maps.py` (Google만) |
| 임베딩 | `1.openai/8.rag/` (내장) | — (미제공) | `9.embeddings/` |
| 비디오 이해 | — | — | `6.video_understanding/` (Google만) |
| 동영상 생성 | Sora(이 저장소엔 미포함) | — | `7.video_generation/` |
