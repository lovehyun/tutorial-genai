# OpenAI 이미지 생성 - 1단계: 프롬프트 → 이미지 → PNG 저장
# pip install openai python-dotenv
#
# 이미지 '생성'(텍스트 → 이미지). 이미지 '이해'(이미지 → 텍스트)는 4.vision/ 참고.
# 앱(7.gpt_image_app*) 이전의 단독 기본 스크립트다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

prompt = '노을 지는 해변, 잔잔한 파도, 수채화 스타일'

# ── gpt-image-1.5 vs gpt-image-2 (둘 다 API 사용법 동일, model= 값만 바꾸면 교체) ──
#   · 해상도   1.5: 최대 1536px(3종 고정)  | 2: 최대 4096px(4K)·커스텀·16:9 비율
#   · 텍스트   1.5: 정확도 ~90~95%         | 2: ~99% + 48개 언어
#   · 속도     1.5: 빠름(~1초)             | 2: ~2~3초 (그리기 전 레이아웃을 '계획')
#   · 투명배경 1.5: 지원 O                  | 2: 미지원 X  (투명 필요하면 반드시 1.5)
#   · 품질     1.5: 우수                     | 2: 최고(현 flagship)
#   · 비용(1024², 2026-05): Low → 1.5 ~$0.01 / 2 ~$0.005,  High → 1.5 ~$0.133 / 2 ~$0.211
#   → 최고 품질·고해상도·정확한 텍스트면 gpt-image-2, 투명배경·속도·저렴한 High면 gpt-image-1.5.
#     (더 저렴한 경량판: gpt-image-1-mini. 상세 표는 ../7.gpt_image_app/README.md)
result = client.images.generate(
    model='gpt-image-1.5',     # 현행 기본값 (위 비교 참고; gpt-image-2 로 바꾸려면 이 값만 변경)
    prompt=prompt,
    size='1024x1024',
    quality='medium',          # low / medium / high / auto
)

# 핵심: gpt-image 는 URL이 아니라 base64(b64_json)로 응답 → 디코드해 파일로 저장
b64 = result.data[0].b64_json
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))

print('저장: output.png')
