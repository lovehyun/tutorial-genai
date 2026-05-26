# OpenAI SDK - 10단계: 구버전 SDK (v0.x) — 참고용
# pip install openai==0.28
#
# 6단계까지는 REST API(chat.completions / responses)를 직접 호출했다.
# 10단계부터는 openai 라이브러리(SDK)를 쓴다 — HTTP 요청·헤더·JSON 파싱을 대신 해 준다.
#
# 이 파일은 '구버전(v0.x)' 스타일. 지금은 v1.x가 표준이지만,
# 인터넷의 옛 예제를 읽을 때를 대비해 모습만 익혀 둔다 (신규 코드는 11단계 사용).

import os
import openai
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

system_prompt = '당신은 친절한 AI 도우미입니다.'

user_message = '안녕, 챗봇!'
# user_message = '오늘 점심 메뉴 추천해줘'

# 구버전: openai.ChatCompletion.create() — 모듈 함수를 직접 호출한다.
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message},
    ],
)

# 구버전 응답은 딕셔너리처럼 접근한다 (REST의 JSON과 동일한 구조).
print('챗봇:', response['choices'][0]['message']['content'])
