# DALL-E 이미지 생성 - 3단계: 여러 프롬프트를 한 번에 (배치 생성)
#
# 2단계 대비 새로 추가된 것:
#   프롬프트 '목록'을 반복문으로 돌며 여러 장을 한 번에 생성한다.
#   프롬프트를 어떻게 쓰느냐에 따라 결과가 달라지는 것을 한눈에 비교할 수 있다.

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

os.makedirs('DATA', exist_ok=True)

# [관전 포인트] 장소·시간·화풍·행동을 조합하면 더 정교한 이미지를 얻는다
#   (예: "at night", "in watercolor style", "a dog running")
prompts = [
    'A cyberpunk cityscape at night with neon lights and flying cars',
    'A cute corgi puppy wearing sunglasses and riding a skateboard',
    'A peaceful mountain lake during sunrise with mist and pine trees',
    'A portrait of a woman in the style of Van Gogh',
    'A delicious Korean bibimbap in a ceramic bowl with colorful vegetables',
]

# 프롬프트 목록을 돌며 한 장씩 생성·저장
for idx, prompt in enumerate(prompts, start=1):
    print(f'[{idx}/{len(prompts)}] 생성 중: {prompt}')
    response = client.images.generate(
        model='dall-e-3',
        prompt=prompt,
        size='1024x1024',
        quality='standard',
        style='vivid',   # "vivid"(선명·강렬) 또는 "natural"(자연스러움)
    )
    img_data = requests.get(response.data[0].url).content
    with open(f'DATA/batch_{idx}.png', 'wb') as f:
        f.write(img_data)
    print(f'  → 저장: DATA/batch_{idx}.png')
