# 6.video_understanding — 비디오 이해

**다른 어떤 벤더 폴더에도 없는 기능입니다.** OpenAI·Anthropic 예제는 텍스트/이미지/PDF 입력까지만
다루지만, Gemini는 영상을 프레임 몇 장으로 쪼개 보는 게 아니라 **시간 흐름·오디오까지 통째로**
이해합니다.

## 파일

| 파일 | 내용 |
|------|------|
| `1.video_understanding.py` | 유튜브 URL을 그대로 넣어 영상 내용 질의 |

## 왜 유튜브 URL부터 시작하나

로컬 영상 파일은 먼저 업로드(`client.files.upload()`)해야 하지만, 유튜브 URL은 `file_uri`에
그대로 넣으면 됩니다 — 별도 파일 준비 없이 바로 실습할 수 있습니다. 로컬 파일을 쓰는 법은
파일 안 주석 참고.

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
