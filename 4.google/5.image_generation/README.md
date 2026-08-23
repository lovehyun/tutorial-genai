# 5.image_generation — 이미지 생성

텍스트로 이미지를 생성합니다. **⚠️ 2026-08-17부로 Imagen 모델이 전부 서비스 종료됐습니다** —
지금은 별도 이미지 전용 모델이 아니라 **Gemini 모델 자체가 이미지도 생성**합니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.image_gen(deprecated).py` | 🛑 **더 이상 동작하지 않음** — Imagen 3 시절 코드, 학습 히스토리로 보존 |
| `2.image_gen.py` | 텍스트 → 이미지 생성 (`gemini-2.5-flash-image`, 현재 동작하는 버전) |
| `3.conversational_editing.py` | 대화형 편집 — "배경만 바꿔줘" 같은 후속 지시로 같은 이미지를 계속 수정 |

이 저장소는 죽은 기능도 삭제하지 않고 `(deprecated)`를 붙여 남겨둡니다(`1.openai/9.multimodal/2.image_generation/1.dall-e(deprecated)/`와 같은 관례) —
"뭐가 왜 바뀌었는지"가 그 자체로 학습 자료이기 때문입니다. `1.image_gen(deprecated).py`와
`2.image_gen.py`를 나란히 열어 diff 삼아 비교해보세요.

## API가 바뀌었습니다

| | 예전 (`1.image_gen(deprecated).py`, 2026-08-17 종료) | 지금 (`2.image_gen.py`) |
|---|---|---|
| 모델 | `imagen-3.0-generate-002` (Imagen 전용) | `gemini-2.5-flash-image` (범용 Gemini) |
| 호출 | `client.models.generate_images()` | `client.interactions.create()` |
| 여러 장 생성 | `number_of_images` 파라미터 | 대화 turn을 반복 |

`client.interactions.create()`는 2025-12에 나온 새 통합 인터페이스입니다(`1.basic` 등에서 쓰는
`client.models.generate_content()`와 별개) — 대화 맥락 유지가 필요한 이미지 편집에서 특히 유용합니다.

## 대화형 편집이 왜 특별한가

`3.conversational_editing.py`는 `previous_interaction_id`로 직전 결과를 가리켜서, "이 그림에서
배경만 바꿔줘" 같은 지시를 계속 이어갈 수 있습니다. 매번 처음부터 다시 설명할 필요 없이,
로봇·의자·책 같은 나머지 요소는 그대로 유지한 채 지시한 부분만 바뀝니다 — 직접 실행해서
저장된 3장(`edit_1_original.png` → `edit_2_sunset.png` → `edit_3_with_cat.png`)을 비교해보세요.

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
