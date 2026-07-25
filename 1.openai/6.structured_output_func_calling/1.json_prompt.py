# 구조화 출력 - 1단계: 프롬프트로 JSON 요청하기 (가장 단순한 방법)
# pip install openai python-dotenv
#
# 왜 '구조화 출력'이 필요한가?
#   지금까지(1~8단계) 모델의 답변은 '자유 형식 텍스트'였다. 사람이 읽기엔 좋지만,
#   코드가 그 답을 받아 처리하려면(DB 저장, 다른 API 호출 등) 곤란하다.
#   → 답을 'JSON' 같은 정해진 구조로 받으면 코드가 바로 꺼내 쓸 수 있다.
#
# 이 단계: 가장 단순하게 '프롬프트로 부탁'해 본다.
#          동작은 하지만 불안정하다는 것을 직접 확인하고 2단계로 넘어간다.

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        # 프롬프트에 "JSON으로 답하라"고 적는 것이 전부다.
        {'role': 'system', 'content': 'JSON 형식으로만 답하세요.'},
        {'role': 'user', 'content': '서울의 인구와 면적을 알려줘.'},
    ],
)

answer = response.choices[0].message.content
print('모델 응답(원본):')
print(answer)

# [관전 포인트] 이 응답을 json.loads로 바로 파싱하면?
#   모델이 ```json ... ``` 코드펜스를 붙이거나 설명 문장을 섞으면 파싱이 깨진다.
#   '부탁'은 강제가 아니라서 실행할 때마다 형식이 달라질 수 있다 → 2단계에서 해결.
try:
    data = json.loads(answer)
    print('\n파싱 성공:', data)
except json.JSONDecodeError as e:
    print('\n파싱 실패! →', e)
