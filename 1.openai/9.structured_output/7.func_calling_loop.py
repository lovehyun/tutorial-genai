# 구조화 출력 - 7단계: Function Calling 전체 흐름 (실행 → 결과 반영)
#
# 5~6단계까지는 모델이 "이 함수를 부르고 싶다"고 알려주는 데서 멈췄다.
# 이 단계: 5단계 코드에 (a) 실제 함수 실행 + (b) 두 번째 API 호출을 추가한다.
#
# 흐름:
#   [1차 호출]  우리 → 모델 : "이 질문에 어떤 함수 부를래?"
#               모델 → 우리 : "get_weather('서울') 불러줘"
#   ─ 우리가 실제 함수 실행 ─
#   [2차 호출]  우리 → 모델 : "결과 이거야. 답변해줘"
#               모델 → 우리 : "서울은 현재 맑고 22도입니다."
#
# 왜 결과를 모델에 '다시' 넘기는가?
#   - 그냥 결과만 보여줄 거면 print() 하면 끝. LLM 필요 없음.
#   - 굳이 다시 넘기는 이유는 세 가지:
#       (a) 자연어로 풀어주기 ('맑음, 22도' → "서울은 맑고 22도예요")
#       (b) 여러 함수 결과 종합·비교 (예: "서울 부산 비교" → 호출 2개 → 종합)
#       (c) 추가 호출이 필요한지 모델이 다시 판단 (실전에선 while 루프로 반복)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [7단계 추가 1] 실제로 실행될 함수 (예시용 가짜 데이터)
def get_weather(city):
    weather = {'서울': '맑음, 22도', '부산': '흐림, 25도'}
    return weather.get(city, '정보 없음')

# 5단계와 동일한 도구 스키마
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

# ── 1차 호출: 5단계와 동일. "어떤 함수 부를래?" 묻기 ─────────
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=messages,
    tools=tools,
)
message = response.choices[0].message

# ── 여기부터 7단계에서 새로 추가되는 부분 ──────────────────

# [7단계 추가 2] 모델의 'tool_call 요청' 메시지를 대화에 그대로 추가
#   이게 있어야 다음 호출에서 모델이 "내가 부른 함수의 결과구나" 하고 맥락을 잇는다.
messages.append(message)

for call in message.tool_calls:
    # [7단계 추가 3] 우리가 실제로 함수를 실행
    args = json.loads(call.function.arguments)   # 인자는 JSON '문자열'로 오므로 파싱
    result = get_weather(**args)
    print(f"실행: get_weather({args}) → {result}")

    # [7단계 추가 4] 실행 결과를 'tool' 역할 메시지로 대화에 추가
    #   tool_call_id 로 "어떤 호출에 대한 결과인지" 모델에게 연결해준다.
    messages.append({
        'role': 'tool',
        'tool_call_id': call.id,
        'content': result,
    })

# 디버깅 분석 코드 --->
# 2차 호출 직전, 모델에게 보낼 messages 가 어떻게 쌓였는지 확인
print('\n[2차 호출 직전 messages 상태]')
for i, m in enumerate(messages):
    print(f'  [{i}] {m}')

# [참고] messages[1] 은 OpenAI SDK 의 Pydantic 객체 그대로 들어가 있어서 좀 지저분해 보인다.
#       같은 내용을 평범한 dict 로 풀어서 만들면 이렇게 생겼다 — API 입장에선 완전히 동일하다.
dict_form = {
    'role': 'assistant',
    'content': message.content,                  # 모델이 텍스트는 안 만들고 함수만 부른 경우 None
    'tool_calls': [
        {
            'id': call.id,
            'type': 'function',
            'function': {
                'name': call.function.name,
                'arguments': call.function.arguments,   # JSON '문자열' 그대로 (dict 아님)
            },
        }
        for call in message.tool_calls
    ],
}
print('\n[참고] messages[1] 을 dict 로 명시적으로 풀면:')
print(dict_form)
# 디버깅 분석 코드 <---

# ── 2차 호출: 결과가 포함된 대화를 다시 보내 '최종 답변' 받기 ──
final = client.chat.completions.create(model='gpt-4o-mini', messages=messages)
print('\n최종 답변:', final.choices[0].message.content)
