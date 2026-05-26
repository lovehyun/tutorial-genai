# OpenAI SDK - 6단계: 신버전 SDK (v1.x) — 현재 표준
# pip install openai
#
# 5단계(구버전)와 같은 일을 v1.x 스타일로. 달라진 점:
#   ① openai.OpenAI()로 client 인스턴스를 먼저 만든다
#   ② client.chat.completions.create() 를 호출한다
#   ③ 응답은 딕셔너리가 아닌 객체 → response.choices[0].message.content 로 접근
#
# 2단계(REST)와 결과는 같지만 코드가 훨씬 간결해진 것을 비교해 보자.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

system_prompt = '당신은 친절한 AI 도우미입니다.'

user_message = '안녕, 챗봇!'
# user_message = '재미있는 과학 상식 하나 알려줘'

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message},
    ],
)

# 객체 속성으로 접근한다 (REST의 ['choices'][0]['message']['content'] 와 비교).
print('챗봇:', response.choices[0].message.content)
