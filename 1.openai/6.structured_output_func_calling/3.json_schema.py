# 구조화 출력 - 3단계: JSON 스키마 (strict 모드)
#
# 2단계 문제: JSON인 것은 보장됐지만 '필드 이름·타입'은 모델 마음대로였다.
#
# 이 단계 해결: response_format에 'json_schema'를 주고 strict=True로 설정한다.
#   → 우리가 정한 스키마(어떤 필드, 어떤 타입, 무엇이 필수)를 모델이 100% 지킨다.
#   → 코드는 data['population']이 '항상 존재하고 정수'라고 믿고 쓸 수 있다.
#
# 스키마는 JSON Schema 표준 문법으로 쓴다 — 아래에 한 줄씩 의미를 달았다.

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 원하는 출력 구조를 미리 정의한다 (도시 이름 / 인구 / 면적)
city_schema = {
    'type': 'object',                       # 최상위는 객체 {}
    'properties': {                         # 객체가 가질 필드들
        'name':       {'type': 'string'},   # 도시 이름 (문자열)
        'population': {'type': 'integer'},  # 인구 (정수)
        'area_km2':   {'type': 'number'},   # 면적 (실수)
    },
    'required': ['name', 'population', 'area_km2'],  # 셋 다 반드시 포함
    'additionalProperties': False,          # 정의하지 않은 필드는 금지
}

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'user', 'content': '서울의 인구와 면적을 알려줘.'},
    ],
    # [관전 포인트] response_format에 위 스키마를 통째로 넘긴다.
    response_format={
        'type': 'json_schema',
        'json_schema': {
            'name': 'city_info',   # 스키마 이름 (임의로 짓는다)
            'strict': True,        # 스키마를 엄격히 강제
            'schema': city_schema,
        },
    },
)

data = json.loads(response.choices[0].message.content)

# 필드가 항상 존재하고 타입도 정확하다고 보장되므로 바로 꺼내 쓴다.
print(f"{data['name']} — 인구 {data['population']:,}명, 면적 {data['area_km2']}㎢")
