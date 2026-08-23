# OpenAI 스트리밍 - 1단계: CLI에서 스트리밍 맛보기 (웹 없이, 콘솔로만)
#
# 2.concept/, 3.simple/ 은 이 스트리밍을 '웹 브라우저'로 흘려보내는 방법을 다룬다.
# 그 전에 스트리밍 자체가 뭔지부터 가장 단순한 형태로 확인한다 — Flask도, SSE도 없다.
#
# 핵심은 딱 한 줄: stream=True.
#   그러면 response가 완성된 답변 하나가 아니라 '토큰 조각(chunk)들의 이터레이터'가 된다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] stream=True — 응답을 다 만들 때까지 기다리지 않고 조각조각 받는다.
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다. 한국어로 답변하세요.'},
        {'role': 'user', 'content': '한국의 사계절을 짧게 한 문단으로 설명해줘.'},
    ],
    stream=True,
)

# [관전 포인트 2] chunk.choices[0].delta.content — 토큰 조각. 비어있을 때도 있어 건너뛴다.
print('챗봇: ', end='', flush=True)
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end='', flush=True)

print()  # 마지막 줄바꿈

# 다음 단계: 이 스트림을 브라우저로 흘려보내는 두 가지 방법 → 2.concept/, 3.simple/
