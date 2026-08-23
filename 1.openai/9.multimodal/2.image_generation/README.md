# 2.image_generation — 이미지 생성

텍스트를 입력으로 받아 **이미지를 생성**합니다 (비전과 짝 — 한쪽은 읽기, 한쪽은 그리기).
DALL-E(구, deprecated) → `4.gpt_image/`(현행 기본) → `5.gpt_image_app*`(앱, 단계별 진화) 순서로 구성됩니다.

| 디렉토리 | 구분 | 내용 |
|----------|------|------|
| [`1.dall-e(deprecated)/`](1.dall-e(deprecated)/) | 구 기본 | DALL-E 이미지 생성 기초 (6단계, 개념 학습용 — 2026-05-12 API 제거) |
| [`2.dall-e-app-edit(deprecated)/`](2.dall-e-app-edit(deprecated)/) | 구 앱 | DALL-E 이미지 편집 웹앱 |
| [`3.dall-e-app-gallery(deprecated)/`](3.dall-e-app-gallery(deprecated)/) | 구 앱 | DALL-E 갤러리 앱 |
| [`4.gpt_image/`](4.gpt_image/) | 기본 | `gpt-image-1.5` 생성·파라미터 비교·투명 배경 — 3개 스크립트 |
| [`5.gpt_image_app/`](5.gpt_image_app/) | 앱 1단계 | 생성 — 프롬프트 → 이미지 (`images.generate`) |
| [`5.gpt_image_app2_inpaint/`](5.gpt_image_app2_inpaint/) | 앱 2단계 | 부분 편집(인페인팅) — 마스크로 영역만 재생성 |
| [`5.gpt_image_app3_consistency/`](5.gpt_image_app3_consistency/) | 앱 3단계 | 일관성 유지 — 기준 이미지로 같은 피사체의 새 장면 |

> 🛑 `dall-e-2`·`dall-e-3`는 2026-05-12자로 API에서 제거되었습니다. 현행 이미지 생성은 `4.gpt_image/`(기본) · `5.gpt_image_app/`(앱)을 참고하세요.
> 모델/가격 비교는 [`5.gpt_image_app/README.md`](5.gpt_image_app/README.md) 참고.
