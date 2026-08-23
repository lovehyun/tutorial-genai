# 4.vision — 이미지 입력(비전)

이미지를 입력으로 받아 분석합니다(이미지 *생성*이 아님 — 생성은 [`../5.image_generation/`](../5.image_generation/)).

## 파일

| 파일 | 내용 |
|------|------|
| `1.vision.py` | 이미지 분석 — URL 또는 로컬 파일 |

## 참고

영상까지 이해하려면 [`../6.video_understanding/`](../6.video_understanding/) 참고 —
이미지는 프레임 하나, 영상은 시간 흐름까지 함께 이해합니다.

## 설치

```bash
pip install google-genai python-dotenv Pillow
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
