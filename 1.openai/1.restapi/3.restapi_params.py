# OpenAI REST API - 3단계: 응답을 조절하는 파라미터
#
# 2단계 대비 추가: 답변의 길이·창의성·반복을 제어하는 파라미터.
# 값을 바꿔가며 응답이 어떻게 달라지는지 비교하는 것이 이 단계의 핵심이다.

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

system_prompt = '당신은 친절한 AI 도우미입니다.'

user_message = '인공지능을 한 문장으로 설명해줘.'
# user_message = '짧은 동화를 하나 지어줘'   # 창의성(temperature) 효과를 보기 좋은 질문

# temperature: 0에 가까울수록 정확·일관, 클수록 창의·다양
#   바꿔보기 → 0.0 (매번 거의 같은 답) / 1.5 (자유분방한 답)
temperature = 0.7

response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ],
        # --- 응답 제어 파라미터 ---
        'temperature': temperature,  # 창의성 (0.0 정확 ~ 2.0 창의)
        'max_tokens': 100,           # 응답의 최대 토큰 수 (길이 제한)
        'top_p': 0.9,                # 확률 상위 토큰만 선택 (1.0 전체 ~ 0.1 상위만)
        'frequency_penalty': 0.5,    # 같은 단어 반복 억제 (-2.0 ~ 2.0)
        'presence_penalty': 0.6,     # 새로운 주제 도입 장려 (-2.0 ~ 2.0)
    },
)

data = response.json()
answer = data['choices'][0]['message']['content']
print(f'[temperature={temperature}] 챗봇:', answer)
