# OpenAI SDK - 9단계: Vision — 이미지 입력 (멀티모달 맛보기)
#
# 8단계까지는 텍스트만 주고받았다. gpt-4o 같은 모델은 이미지도 입력으로 받는다.
# 핵심: user 메시지의 content를 문자열이 아니라
#       [{'type':'text', ...}, {'type':'image_url', ...}] 리스트로 구성한다.
#
# 이미지는 URL 또는 base64 Data URL로 전달 (여기서는 로컬 파일 → base64).
# 멀티모달은 10.multimodal 폴더에서 본격적으로 다룬다.

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 분석할 이미지 — 한 줄만 활성화해 바꿔보세요
image_path = 'squats_good.jpg'
# image_path = 'squats_bad.jpg'   # 잘못된 자세와 비교해 보세요

# 이미지에 던질 질문
question = '이 운동 자세에서 잘못된 점이나 개선할 부분이 있나요?'
# question = '이 운동 자세를 100점 만점으로 평가해줘'

def encode_image_to_base64(path):
    """로컬 이미지를 base64 Data URL 형식으로 인코딩한다."""
    with open(path, 'rb') as image_file:
        base64_bytes = base64.b64encode(image_file.read()).decode('utf-8')
        return f'data:image/jpeg;base64,{base64_bytes}'

response = client.chat.completions.create(
    model='gpt-4o',  # vision 지원 모델 (gpt-4o-mini 도 가능)
    messages=[
        {'role': 'system', 'content': '당신은 운동 자세를 평가하는 피트니스 트레이너입니다.'},
        {
            'role': 'user',
            # content가 문자열이 아니라 '리스트' — 텍스트와 이미지를 함께 담는다
            'content': [
                {'type': 'text', 'text': question},
                {'type': 'image_url', 'image_url': {'url': encode_image_to_base64(image_path)}},
            ],
        },
    ],
    max_tokens=1000,
)

print('GPT 자세 분석 결과:')
print(response.choices[0].message.content)
