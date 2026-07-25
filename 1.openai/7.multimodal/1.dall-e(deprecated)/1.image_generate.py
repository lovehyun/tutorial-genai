# DALL-E 이미지 생성 - 1단계: 기본 이미지 생성
# pip install openai python-dotenv
#
# OpenAI 이미지 생성 API의 가장 단순한 사용. 텍스트 프롬프트 → 이미지 1장.
# 생성 결과를 DATA/generated_image.png 로 저장한다 (4·5단계가 이 파일을 사용).
#
# 참고: 이미지 생성 모델 3종(dall-e-2/3, gpt-image-1) 비교는 README.md 참고.

import os
import urllib.request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

os.makedirs('DATA', exist_ok=True)

# [관전 포인트] images.generate — 텍스트 프롬프트로 이미지를 생성한다
#   model   : "dall-e-3", "dall-e-2"
#   prompt  : 이미지 설명 (영어로 상세할수록 품질이 좋다)
#   size    : "1024x1024", "1024x1792", "1792x1024" (dall-e-3 기준)
#   quality : "standard" 또는 "hd" (hd는 더 선명하지만 비쌈)
#   n       : 생성 장 수 (dall-e-3은 1장 고정, dall-e-2는 최대 10장)
response = client.images.generate(
    model='dall-e-3',
    prompt='A cute baby sea otter',
    size='1024x1024',
    quality='standard',
    n=1,
)

# [관전 포인트] 응답에는 이미지 자체가 아니라 '이미지 URL'이 담겨 온다
image_url = response.data[0].url
print('생성된 이미지 URL:', image_url)

# URL의 이미지를 내려받아 저장 (4·5단계가 이 파일을 사용한다)
urllib.request.urlretrieve(image_url, 'DATA/generated_image.png')
print('저장 완료: DATA/generated_image.png')
