# DALL-E 이미지 생성 (deprecated)

> 🛑 **이 폴더의 dall-e 예제는 더 이상 동작하지 않습니다.**
> OpenAI가 2025-11-14에 단종을 공지하고, **2026-05-12자로 `dall-e-2`·`dall-e-3`를
> API에서 완전히 제거**했습니다. 예제는 '개념 학습용'으로 보존합니다.
>
> ⚠️ **모델명만 바꾼다고 동작하지 않습니다.** gpt-image 계열은 응답이 URL이 아니라
> base64이고(`url` → `b64_json`), `quality`/`style` 등 파라미터도 다릅니다. 응답 처리와
> 파라미터까지 함께 고쳐야 하며, 그 완성형이 같은 폴더의 `6.gpt_image1.py`,
> 본격 활용은 `8.gpt_image_app/`에 있습니다.
> 현행 이미지 모델·가격은 [8.gpt_image_app/README.md](../8.gpt_image_app/README.md) 참고.

OpenAI 이미지 API의 기초를, 한 단계에 개념 하나씩 더해가며 배웁니다.

## 학습 순서

| 파일 | 이 단계에서 새로 배우는 것 |
|------|---------------------------|
| `1.image_generate.py` | 기본 — 프롬프트로 이미지 1장 생성·저장 |
| `2.image_models.py` | 함수로 묶고 dall-e-2 / dall-e-3 결과 비교 |
| `3.image_batch.py` | 프롬프트 목록을 반복해 여러 장 배치 생성 |
| `4.image_mask.py` | 인페인팅용 마스크(흑백 이미지) 만들기 |
| `5.image_edit.py` | 마스크로 이미지 일부만 편집(인페인팅) |
| `6.gpt_image1.py` | 최신 모델 gpt-image-1 — dall-e와의 API 차이(base64 응답) |

### 실행 순서 (의존성)

편집 단계는 앞 단계의 산출물이 필요합니다:

```
1.image_generate.py  →  DATA/generated_image.png 생성
4.image_mask.py      →  DATA/mask.png 생성 (generated_image.png 크기를 참조)
5.image_edit.py      →  위 두 파일을 사용해 편집
```

`1 → 4 → 5` 순서로 실행하세요. (2·3은 독립적으로 실행 가능)

## OpenAI 이미지 생성 모델 (중요 — 변경됨)

> ⚠️ **dall-e 단종 일정**: 2025-11-14 단종 공지 → **2026-05-12 API에서 완전 제거**.
> 이 폴더의 1~5단계 예제(dall-e 사용)는 그대로는 실행되지 않습니다.
> 6단계(`6.gpt_image1.py`)의 `gpt-image-1`은 동작하지만 2026-10-23 종료 예정입니다.

| 모델 | 출시 | 상태 |
|------|------|------|
| `dall-e-2` | 2022 | 2026-05-12 API 제거 |
| `dall-e-3` | 2023 | 2026-05-12 API 제거 |
| `gpt-image-1` | 2025 | 2026-10-23 종료 예정 |
| `gpt-image-1.5` / `gpt-image-2` | 2026 | 현행 |

현재 사용 가능한 이미지 모델 목록과 **가격 비교**는
[`8.gpt_image_app/README.md`](../8.gpt_image_app/README.md)에 정리되어 있습니다.

이 폴더는 이미지 생성의 '개념'(생성·마스크·인페인팅)을 익히는 학습용으로 남겨둡니다.
1~5단계를 실제로 돌리려면 모델명 외에 응답 형식(url→base64)·파라미터까지 바꿔야 하며,
그 완성형이 6단계 `6.gpt_image1.py`입니다.

## 설치 및 실행

```bash
pip install openai pillow requests python-dotenv
python 1.image_generate.py
```

API 키는 `1.openai/.env`(이 폴더 기준 `../../.env`)에 설정합니다: `OPENAI_API_KEY=sk-...`
