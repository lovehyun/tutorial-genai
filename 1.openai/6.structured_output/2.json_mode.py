# 구조화 출력 - 2단계: JSON 모드 (response_format)
#
# 1단계 문제: 프롬프트로 '부탁'만 해서 형식이 들쭉날쭉, 파싱이 깨질 수 있었다.
#
# 이 단계 해결: response_format={"type": "json_object"} 옵션을 준다.
#   → 모델이 '문법적으로 올바른 JSON'을 반환하도록 API가 보장한다.
#     코드펜스(```)나 설명 문장이 섞이지 않는다.
#
# 남은 한계: JSON인 것은 보장되지만 '어떤 필드가 들어올지'는 보장 안 된다.
#            (population? area? 필드 이름이 매번 다를 수 있음) → 3단계에서 해결.

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        # JSON 모드는 메시지에 'JSON'이라는 단어가 포함돼 있어야 동작한다.
        {'role': 'system', 'content': 'JSON 형식으로 답하세요.'},
        {'role': 'user', 'content': '서울의 인구와 면적을 알려줘.'},
    ],
    # [관전 포인트] 이 한 줄이 핵심 — 출력이 항상 올바른 JSON임을 API가 보장한다.
    response_format={'type': 'json_object'},
)

answer = response.choices[0].message.content

# 이제 json.loads가 안전하게 동작한다 (1단계처럼 깨질 걱정이 없다).
data = json.loads(answer)
print('파싱 성공:', data)
print('키 목록:', list(data.keys()))  # 단, 키 '이름'은 여전히 모델이 정한다
