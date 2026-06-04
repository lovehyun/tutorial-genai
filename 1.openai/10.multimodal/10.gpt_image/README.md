# 10.gpt_image — 이미지 생성 기초

**이미지 생성 = 텍스트를 입력으로 받아 이미지를 만드는 것** (텍스트 → 이미지).
앱(`11.gpt_image_app*`) 이전의 **단독 기본 스크립트**다. 이미지 *이해*(이미지 → 텍스트)는 [`../4.vision/`](../4.vision/).

## 핵심
- `images.generate(model, prompt, size, quality)` 호출
- 응답은 **URL이 아니라 base64**(`result.data[0].b64_json`) → 디코드해 파일 저장
- 모델: `gpt-image-1.5`(현행). `model=` 만 바꾸면 `gpt-image-2` 등으로 교체
- `background='transparent'` 로 투명 배경 PNG 생성 가능

## 파일
| 파일 | 내용 |
|------|------|
| `1.image_generate.py` | 프롬프트 → 생성 → `output.png` 저장 (가장 기본) |
| `2.image_params.py` | `size` / `quality` 비교 |
| `3.image_transparent.py` | 투명 배경 PNG (아이콘/스티커) |

## 실행
```bash
cd 1.openai/10.multimodal/10.gpt_image
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.image_generate.py    # output.png
python 2.image_params.py      # robot_low.png, robot_medium.png, robot_wide.png
python 3.image_transparent.py # apple.png
```
> 생성된 `*.png` 는 `.gitignore` 처리됨. 이미지 모델/가격 비교는 [`../11.gpt_image_app/README.md`](../11.gpt_image_app/README.md).

## 다음
- 웹앱 + 편집/인페인팅/일관성 → [`../11.gpt_image_app/`](../11.gpt_image_app/) (단계별)
