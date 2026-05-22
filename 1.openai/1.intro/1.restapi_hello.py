# OpenAI REST API - 1단계: 가장 단순한 호출
# pip install requests python-dotenv
#
# 목표: API에 요청을 보내면 "무엇이 돌아오는지" 직접 눈으로 본다.
#       응답을 가공하지 않고 JSON 통째로 출력한다.

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

# 모델에 보낼 질문 — 한 줄만 활성화해 바꿔가며 테스트해 보세요
user_message = '안녕, 챗봇!'
# user_message = '파이썬이 뭐야?'
# user_message = '1부터 100까지 더하면 얼마야?'

# Chat Completions 엔드포인트에 POST 요청
response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        # messages: 모델에 보내는 대화 메시지 목록.
        # 지금은 사용자가 보내는 user 메시지 하나뿐이다 (role은 2단계에서 설명).
        'messages': [
            {'role': 'user', 'content': user_message},
        ],
    },
)

# 응답 JSON을 통째로 출력 — 어떤 구조로 돌아오는지 확인한다.
# 답변 텍스트는 choices[0].message.content 안에 들어 있다 → 2단계에서 추출.
print(response.json())
