# 구조화 출력 - 6단계: 5단계 검증 (tool_choice='auto' 의 자동 판단 확인)
#
# 5단계에서는 도구가 트리거되는 질문 하나만 봤다.
# 이번엔 같은 설정으로 두 가지 질문을 던져서 모델이 어떻게 분기하는지 확인한다:
#   - 함수가 필요한 질문 → message.tool_calls 에 호출 정보가 담김
#   - 함수가 필요 없는 질문 → tool_calls 는 비고, message.content 에 일반 답변
#
# 즉, "무조건 함수를 부르는 게 아니라 모델이 스스로 판단한다"는 점을 눈으로 확인하는 단계.

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 5단계와 동일한 도구 정의
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

# [관전 포인트] 두 가지 질문 — 하나는 도구가 필요하고, 하나는 필요 없다.
test_questions = [
    '서울 날씨 어때?',          # → get_weather 호출이 예상됨
    '파이썬 리스트가 뭐야?',     # → 함수 없이 일반 답변이 예상됨
]

for q in test_questions:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': q}],
        tools=tools,
        tool_choice='auto',     # 모델이 스스로 함수 사용 여부를 판단
    )
    message = response.choices[0].message

    print(f"\n[질문] {q}")
    if message.tool_calls:
        call = message.tool_calls[0]
        print('  → 함수 호출 판단:', call.function.name)
        print('  → 인자:', json.loads(call.function.arguments))
    else:
        print('  → 일반 답변:', message.content)
