# OpenAI SDK - 15단계: Responses API를 SDK로 호출 (기본)
# pip install openai python-dotenv
#
# 5단계는 raw HTTP(requests)로 /v1/responses 를 호출했다.
# 15단계는 같은 일을 openai SDK로 한다. SDK가 줄여주는 것:
#   - 엔드포인트·헤더·json.loads 를 직접 다룰 필요가 없다.
#   - 응답 텍스트가 response.output_text 한 줄로 바로 나온다
#     (raw HTTP에서는 output[0].content[0].text 로 직접 파고들어야 했다).
#
# 멀티턴 체인(previous_response_id 활용)은 16.response_multiturn.py 에서 다룬다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] client.responses.create — chat.completions와 다른 새 엔드포인트
#   input은 문자열 한 줄로 충분 (messages 리스트 불필요)
response = client.responses.create(
    model='gpt-4o-mini',
    input='대한민국의 수도는 어디야?',
)

# [관전 포인트 2] response.output_text — SDK가 output[0].content[0].text 를 한 줄로 노출
print('챗봇:', response.output_text)
print('response_id:', response.id)
