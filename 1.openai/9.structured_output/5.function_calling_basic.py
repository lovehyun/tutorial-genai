# 구조화 출력 - 5단계: Function Calling 입문 (모델이 '함수 호출'을 판단)
#
# 4단계까지는 출력의 '모양'을 고정했다. 5단계부터는 한 발 더 나간다:
#   모델이 "이 질문엔 함수를 써야겠다"고 스스로 판단하고,
#   그 함수에 넘길 인자를 구조화된 형태로 만들어 준다.
#
# 이 단계: 함수를 '실제로 실행'하진 않는다. 모델이 무엇을 호출하려는지 확인만 한다.
#          (실행하고 결과를 돌려주는 전체 흐름은 6단계)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [관전 포인트 1] 모델에게 "이런 함수를 쓸 수 있다"고 알려주는 도구 정의(스키마).
#   실제 코드가 아니라 '설명서'다 — 함수 이름, 설명, 어떤 인자를 받는지.
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': '특정 도시의 현재 날씨를 조회한다',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {'type': 'string', 'description': '도시 이름'},
                },
                'required': ['city'],
            },
        },
    }
]

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'user', 'content': '서울 날씨 어때?'},
    ],
    tools=tools,
    # tool_choice='auto' : 함수를 쓸지 말지 모델이 판단한다 (기본값).
    #   참고: 'none'(쓰지 마라) / {함수 지정}(반드시 그 함수)도 줄 수 있다.
    tool_choice='auto',
)

message = response.choices[0].message

# [관전 포인트 2] 모델이 함수를 쓰기로 했으면 message.tool_calls 에 내용이 담긴다.
#   (함수가 필요 없는 질문이면 tool_calls는 비고, message.content에 일반 답변이 온다.)
if message.tool_calls:
    call = message.tool_calls[0]
    print('모델이 호출하려는 함수:', call.function.name)
    # 인자는 JSON '문자열'로 온다 → 딕셔너리로 파싱해서 확인
    print('모델이 만든 인자:', json.loads(call.function.arguments))
else:
    print('함수 없이 일반 답변:', message.content)
