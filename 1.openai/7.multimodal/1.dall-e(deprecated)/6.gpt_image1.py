# DALL-E 이미지 생성 - 6단계: 최신 모델 gpt-image-1
# pip install openai python-dotenv
#
# 5단계까지는 dall-e-2/3을 썼다. 6단계는 최신 이미지 모델 gpt-image-1을 쓴다.
#
# 1단계(dall-e-3)와 비교한 핵심 차이:
#   - 응답에 이미지 URL이 없다. 항상 base64(b64_json) 문자열로 온다.
#     → urllib로 '내려받기'가 아니라, base64를 '디코딩'해서 저장한다.
#   - quality 값이 다르다: low / medium / high / auto
#   - 품질이 가장 좋고, 특히 이미지 안의 텍스트 렌더링이 우수하다.
#
# 모델 3종(dall-e-2/3, gpt-image-1) 비교는 README.md 참고.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

os.makedirs('DATA', exist_ok=True)

response = client.images.generate(
    model='gpt-image-1',
    # 텍스트가 들어간 프롬프트 — gpt-image-1의 강점(글자 렌더링)을 확인하기 좋다
    prompt='A poster with the bold text "HELLO AI" on a neon city background',
    size='1024x1024',
    quality='high',   # gpt-image-1: low / medium / high / auto
)

# [관전 포인트] dall-e와 달리 .url 이 없다 — .b64_json (base64 문자열)로 온다
b64 = response.data[0].b64_json

# base64 문자열을 실제 이미지 바이트로 '디코딩'해서 저장한다
image_bytes = base64.b64decode(b64)
with open('DATA/gpt_image1.png', 'wb') as f:
    f.write(image_bytes)
print('저장 완료: DATA/gpt_image1.png')
