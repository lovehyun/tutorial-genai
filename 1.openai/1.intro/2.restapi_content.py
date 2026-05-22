# OpenAI REST API - 2단계: 응답에서 답변만 꺼내기 + 역할(role)
#
# 1단계 대비 추가: ① 답변 텍스트(content)만 추출  ② system 역할 추가
#
# [메시지의 역할(role) 3가지]
#   system    : 챗봇의 정체성·말투·규칙을 정한다 (대화 시작 전 1회 설정)
#   user      : 사용자가 보내는 질문/요청
#   assistant : 모델이 응답한 메시지 (지난 답변을 다시 넣을 때 사용 → 8단계)

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

# system: 챗봇의 성격 — 한 줄만 활성화해 바꿔보세요 (응답 말투가 달라진다)
system_prompt = '당신은 친절한 AI 도우미입니다.'
# system_prompt = '당신은 최고급 호텔의 요리사입니다. 요리 관점에서 답하세요.'
# system_prompt = '당신은 모든 답을 짧은 시(詩)로 답하는 시인입니다.'

# user: 사용자 질문 — 바꿔가며 테스트해 보세요
user_message = '안녕, 챗봇!'
# user_message = '김치찌개 맛있게 끓이는 법 알려줘'

response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ],
    },
)

data = response.json()

# 1단계에서 본 JSON 구조를 따라 답변 텍스트만 꺼낸다.
# choices[0] → message → content 에 실제 답변이 들어 있다.
answer = data['choices'][0]['message']['content']
print('챗봇:', answer)
