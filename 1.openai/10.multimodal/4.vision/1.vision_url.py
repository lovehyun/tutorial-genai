# OpenAI Vision - 1단계: 이미지 URL을 모델에게 보여주고 설명 듣기
# pip install openai python-dotenv
#
# Vision(비전) = 이미지를 '입력'으로 받아 이해하는 것 (이미지 → 텍스트).
#   ↔ 이미지 '생성'(텍스트 → 이미지)은 9.gpt_image/ 참고.
#
# 핵심: chat.completions 에 content 를 '블록 리스트'로 준다 — 텍스트 블록 + 이미지 블록.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 공개 이미지 URL (OpenAI 공식 예제에 쓰이는 자연 풍경 사진)
image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg'

response = client.chat.completions.create(
    model='gpt-4o-mini',   # 비전 가능한 챗 모델 (더 정밀하게는 gpt-4o)
    messages=[
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': '이 이미지를 한국어로 설명해줘.'},
                {'type': 'image_url', 'image_url': {'url': image_url}},
            ],
        }
    ],
)

print(response.choices[0].message.content)
