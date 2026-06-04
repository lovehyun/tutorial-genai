# OpenAI 이미지 생성 - 1단계: 프롬프트 → 이미지 → PNG 저장
# pip install openai python-dotenv
#
# 이미지 '생성'(텍스트 → 이미지). 이미지 '이해'(이미지 → 텍스트)는 4.vision/ 참고.
# 앱(11.gpt_image_app*) 이전의 단독 기본 스크립트다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

prompt = '노을 지는 해변, 잔잔한 파도, 수채화 스타일'

result = client.images.generate(
    model='gpt-image-1.5',     # 현행 이미지 모델 (model= 만 바꾸면 gpt-image-2 등으로 교체)
    prompt=prompt,
    size='1024x1024',
    quality='medium',          # low / medium / high / auto
)

# 핵심: gpt-image 는 URL이 아니라 base64(b64_json)로 응답 → 디코드해 파일로 저장
b64 = result.data[0].b64_json
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('저장: output.png')
