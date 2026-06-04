# OpenAI 이미지 생성 - 3단계: 투명 배경 이미지
# pip install openai python-dotenv
#
# gpt-image-1.5 는 background='transparent' 로 배경이 비치는 PNG를 만든다.
# 아이콘·스티커·로고처럼 배경을 빼야 할 때 유용하다. (반드시 PNG로 저장)

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

result = client.images.generate(
    model='gpt-image-1.5',
    prompt='빨간 사과 아이콘, 단순한 플랫 디자인',
    size='1024x1024',
    quality='medium',
    background='transparent',   # 투명 배경 (opaque / auto 도 가능)
)

with open('apple.png', 'wb') as f:
    f.write(base64.b64decode(result.data[0].b64_json))
print('저장: apple.png (투명 배경 PNG)')
