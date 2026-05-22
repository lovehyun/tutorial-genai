# 구조화 출력 - 6단계: Function Calling 전체 흐름 (실행 → 결과 반영)
#
# 5단계: 모델이 "get_weather('서울')을 부르고 싶다"고 알려주는 데서 멈췄다.
#
# 이 단계: 그 함수를 실제로 실행하고, 결과를 모델에게 돌려줘서
#          모델이 그 결과를 바탕으로 '최종 답변'을 만들게 한다.
#
# Function Calling의 핵심 왕복:
#   ① 질문 + 도구 목록 전송  → ② 모델: "이 함수 불러"  → ③ 우리가 함수 실행
#   → ④ 실행 결과를 tool 메시지로 다시 전송  → ⑤ 모델: 결과를 반영한 최종 답변

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 실제로 실행될 함수 (여기서는 예시용 가짜 데이터)
def get_weather(city):
    weather = {'서울': '맑음, 22도', '부산': '흐림, 25도'}
    return weather.get(city, '정보 없음')

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': '특정 도시의 현재 날씨를 조회한다',
            'parameters': {
                'type': 'object',
                'properties': {'city': {'type': 'string', 'description': '도시 이름'}},
                'required': ['city'],
            },
        },
    }
]

# 대화 메시지 목록 — 단계가 진행되며 여기에 메시지가 쌓인다.
messages = [{'role': 'user', 'content': '서울 날씨 어때?'}]

# ① 질문 + 도구 목록 전송
response = client.chat.completions.create(model='gpt-4o-mini', messages=messages, tools=tools)
message = response.choices[0].message

# ② 모델이 함수 호출을 요청 → 그 메시지를 대화에 그대로 추가한다.
messages.append(message)

for call in message.tool_calls:
    # ③ 우리가 함수를 실제로 실행한다.
    args = json.loads(call.function.arguments)
    result = get_weather(**args)
    print(f"실행: get_weather({args}) → {result}")

    # ④ 실행 결과를 'tool' 역할 메시지로 추가한다.
    #    tool_call_id로 '어떤 호출의 결과인지' 모델에게 연결해 준다.
    messages.append({
        'role': 'tool',
        'tool_call_id': call.id,
        'content': result,
    })

# ⑤ 함수 결과가 포함된 대화를 다시 보내 최종 답변을 받는다.
final = client.chat.completions.create(model='gpt-4o-mini', messages=messages)
print('\n최종 답변:', final.choices[0].message.content)
