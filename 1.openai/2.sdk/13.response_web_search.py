# OpenAI SDK - 13단계: Responses API 내장 도구 — web_search
#
# ../7.function_calling 폴더에서는 '내가 만든' 함수를 모델이 호출하도록 했다
# (get_weather 같은 예시 — 실제로 실행하는 코드는 내가 직접 짜야 했다).
#
# 13단계는 다르다: web_search는 OpenAI가 '이미 만들어서 서버에서 실행해주는' 도구다.
#   - 함수 스키마를 내가 정의할 필요 없음 (tools=[{'type': 'web_search'}] 한 줄)
#   - 모델이 실제로 검색까지 수행하고, 그 결과를 반영한 답을 바로 준다
#   - 학습 데이터 마감 이후의 '최신 정보'도 답할 수 있게 된다
#
# 참고: 도구 이름(web_search)은 OpenAI가 API를 발전시키며 바뀔 수 있다.
#       오류가 나면 최신 문서에서 정확한 tool type을 확인할 것.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트] tools에 web_search 하나만 추가 — 나머지는 10단계(sdk_response.py)와 동일.
response = client.responses.create(
    model='gpt-4o-mini',
    input='오늘 서울 날씨와 미세먼지 상황을 알려줘.',
    tools=[{'type': 'web_search'}],
)

print('챗봇:', response.output_text)

# [참고] 어떤 검색을 했는지도 response.output 안에 web_search_call 항목으로 남아있다.
#        (질문이 실시간 정보가 필요 없으면 모델이 검색을 아예 안 할 수도 있다 — 정상 동작.)
