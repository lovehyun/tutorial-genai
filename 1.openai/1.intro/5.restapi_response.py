# OpenAI REST API - 5단계: Responses API 입문
# pip install requests python-dotenv
#
# 1~4단계는 'Chat Completions' API(/v1/chat/completions)를 썼다.
# 5~6단계는 OpenAI의 신형 'Responses' API(/v1/responses)를 다룬다.
#
# Responses API의 큰 특징 두 가지:
#   ① input이 문자열 한 줄이어도 된다 (messages 리스트를 안 만들어도 됨).
#   ② 서버가 응답을 저장한다(기본 store=true). 다음 호출에서 previous_response_id로
#      참조하면 대화 맥락이 이어진다 → 6단계에서 다룸.
#
# 이 단계: Responses API의 '가장 단순한' 호출 한 번만 본다.

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

# 질문을 바꿔가며 테스트해 보세요
user_input = '대한민국의 수도는 어디야?'
# user_input = '파이썬을 한 줄로 설명해줘'

response = requests.post(
    # [관전 포인트 1] 엔드포인트가 다르다 — /v1/chat/completions 가 아니라 /v1/responses
    'https://api.openai.com/v1/responses',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        # [관전 포인트 2] input은 문자열 한 줄로 충분 — messages 리스트 불필요
        'input': user_input,
    },
)

data = response.json()

# [관전 포인트 3] 응답 구조 — output[0].content[0].text 에 답변 텍스트가 있다
#   output 은 메시지·도구호출 등을 담는 배열이고, message 안에 content 배열이 있고,
#   그 안의 output_text 항목에 실제 텍스트가 있다.
#   (SDK를 쓰면 response.output_text 한 줄로 같은 결과를 얻을 수 있다 — raw HTTP에는 그 필드가 없다)
answer = data['output'][0]['content'][0]['text']
print('챗봇:', answer)

# [관전 포인트 4] 응답에 id가 있다 — 다음 호출에서 previous_response_id로 참조 가능
print('response_id:', data['id'])
