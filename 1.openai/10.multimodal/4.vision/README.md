# 4.vision — 비전 기초 (이미지 이해)

**Vision = 이미지를 입력으로 받아 이해하는 것** (이미지 → 텍스트).
앱(`5.vision_app*`) 이전의 **단독 기본 스크립트**다. 이미지 *생성*(텍스트 → 이미지)은 [`../10.gpt_image/`](../10.gpt_image/).

## 핵심
- 비전 가능한 챗 모델(`gpt-4o-mini` / `gpt-4o`)에 `chat.completions` 로 호출
- `content` 를 **블록 리스트**로: `{"type":"text"}` + `{"type":"image_url"}`
- 이미지 소스: **URL** 또는 **로컬 파일(base64 data URL)**

## 파일
| 파일 | 내용 |
|------|------|
| `1.vision_url.py` | 인터넷 이미지 URL → 설명 |
| `2.vision_localfile.py` | 로컬 파일 → base64 인코딩 → 분석 |
| `3.vision_question.py` | 한 이미지에 OCR·색상·분위기 등 여러 질문 |

## 실행
```bash
cd 1.openai/10.multimodal/4.vision
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.vision_url.py
# 2,3 번은 같은 폴더에 sample.jpg(분석할 이미지)를 두고 실행
python 2.vision_localfile.py
python 3.vision_question.py
```

## 다음
- 웹앱으로 확장 → [`../5.vision_app/`](../5.vision_app/) (업로드·클립보드·음성입력 등 단계별)
