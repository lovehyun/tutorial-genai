# OpenAI Vision - 2단계: 로컬 이미지 파일을 분석하기
# pip install openai python-dotenv
#
# 1단계는 인터넷 URL이었다. 실무에선 '내 파일'을 보내는 경우가 많다.
# 핵심: 로컬 파일은 base64 로 인코딩해 'data URL' 형태로 넣는다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

IMAGE_PATH = 'sample.jpg'   # 같은 폴더에 분석할 이미지를 두세요 (jpg/png)


def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


b64 = encode_image(IMAGE_PATH)

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': '이 이미지에 무엇이 있는지 설명해줘.'},
                # 로컬 파일은 data URL(data:image/...;base64,...) 형태로 전달
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
            ],
        }
    ],
)

print(response.choices[0].message.content)
