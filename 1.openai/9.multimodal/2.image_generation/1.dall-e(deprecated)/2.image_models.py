# DALL-E 이미지 생성 - 2단계: 함수로 묶고 모델 비교하기
#
# 1단계 대비 새로 추가된 것:
#   ① 이미지 생성을 함수(generate_image)로 분리 → 재사용 가능
#   ② model 인자를 바꿔 dall-e-2 와 dall-e-3 의 결과를 비교
#
# 같은 프롬프트라도 모델에 따라 품질·화풍이 다르다 — 두 결과 파일을 열어 비교해 보자.

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

os.makedirs('DATA', exist_ok=True)

# [관전 포인트] model을 인자로 받는 함수 — 호출부에서 모델만 바꿔 쓴다
def generate_image(prompt, model, filename):
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size='1024x1024',
        n=1,
    )
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    with open(f'DATA/{filename}', 'wb') as f:
        f.write(img_data)
    print(f'[{model}] 저장 완료: DATA/{filename}')

prompt = 'A futuristic cityscape with flying cars'

# 같은 프롬프트를 두 모델로 생성해 결과를 비교
generate_image(prompt, 'dall-e-2', 'compare_dalle2.png')
generate_image(prompt, 'dall-e-3', 'compare_dalle3.png')
