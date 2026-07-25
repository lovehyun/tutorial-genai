# DALL-E 이미지 생성 - 5단계: 마스크로 이미지 편집 (인페인팅)
# pip install openai pillow requests python-dotenv
#
# 4단계 대비 새로 추가된 것:
#   4단계에서 만든 마스크(DATA/mask.png)와 원본 이미지를 images.edit 에 함께 넣어,
#   마스크의 흰색 영역만 프롬프트대로 새로 그린다.
#
# 실행 전 준비 (순서대로):
#   1단계 실행 → DATA/generated_image.png 생성
#   4단계 실행 → DATA/mask.png 생성
#
# 참고: 편집(images.edit)은 dall-e-2·gpt-image-1만 지원한다 (dall-e-3은 불가).
#       모델 비교는 README.md 참고.

import os
import requests
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] images.edit는 투명도 채널이 있는 RGBA 이미지를 요구한다
#   → 원본을 RGBA로 변환해 저장
with Image.open('DATA/generated_image.png') as img:
    img.convert('RGBA').save('DATA/generated_image_rgba.png')

# [관전 포인트 2] 원본 + 마스크 + 프롬프트를 함께 전달
#   마스크의 흰색 영역이 prompt 내용으로 다시 그려진다
response = client.images.edit(
    image=open('DATA/generated_image_rgba.png', 'rb'),
    mask=open('DATA/mask.png', 'rb'),
    prompt='A cute baby sea otter wearing a beret',
    n=2,
    size='1024x1024',
)

# 편집 결과 저장
for idx, data in enumerate(response.data):
    img_data = requests.get(data.url).content
    with open(f'DATA/edited_{idx}.png', 'wb') as f:
        f.write(img_data)
    print(f'편집 결과 저장: DATA/edited_{idx}.png')
