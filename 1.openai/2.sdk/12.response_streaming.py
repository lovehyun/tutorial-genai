# OpenAI SDK - 12단계: Responses API 스트리밍 (stream=True)
#
# 10단계(sdk_response.py)는 완성된 답을 한 번에 받았다 — 응답이 끝날 때까지 기다림.
# 12단계는 토큰이 만들어지는 대로 조금씩 흘려받는다 (SSE와 같은 개념, ../4.streaming 참고).
#
# chat.completions의 스트리밍(../4.streaming)과 이벤트 모양이 다르다:
#   - chat.completions: chunk.choices[0].delta.content 를 계속 이어붙임
#   - responses:        event.type 으로 여러 종류의 이벤트가 오고,
#                        텍스트 조각은 'response.output_text.delta' 이벤트의 .delta 에 담김

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] stream=True — 완성된 응답 대신 이벤트 스트림(iterator)을 돌려받는다.
stream = client.responses.create(
    model='gpt-4o-mini',
    input='한국의 사계절을 짧게 한 문단으로 설명해줘.',
    stream=True,
)

print('챗봇: ', end='', flush=True)

# [관전 포인트 2] 이벤트 종류가 여러 개다 — 텍스트 조각만 골라서 출력한다.
#   (다른 이벤트: response.created, response.output_text.done, response.completed 등)
for event in stream:
    if event.type == 'response.output_text.delta':
        print(event.delta, end='', flush=True)

print()  # 마지막 줄바꿈
