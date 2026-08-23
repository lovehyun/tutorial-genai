# OpenAI Vision - 3단계: 한 이미지에 '구체적인 질문' 여러 개 던지기
# pip install openai python-dotenv
#
# 단순 설명을 넘어, 같은 이미지에 대해 OCR·색상·분위기 등 원하는 것을 물어본다.
# 함수화해서 이미지를 한 번만 인코딩하고 질문만 바꿔 재사용한다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

IMAGE_PATH = 'sample.jpg'   # 같은 폴더에 이미지를 두세요


def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def ask_about_image(question, b64):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': question},
                    {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}},
                ],
            }
        ],
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    b64 = encode_image(IMAGE_PATH)
    questions = [
        '이미지에 글자가 있으면 그대로 읽어줘 (OCR).',
        '주요 색상 3개를 알려줘.',
        '전체 분위기를 한 단어로 표현하면?',
    ]
    for q in questions:
        print(f'Q: {q}')
        print(f'A: {ask_about_image(q, b64)}\n')
