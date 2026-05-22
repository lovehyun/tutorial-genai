# OpenAI SDK - 7단계: SDK에서 파라미터 적용
#
# 6단계 대비 추가: 3단계(REST)에서 다룬 응답 제어 파라미터를 SDK 방식으로.
# REST에서는 json={...} 안에 넣었지만, SDK에서는 create()의 인자로 직접 전달한다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 모델 — 한 줄만 활성화해 바꿔보세요 (표준/추론 모델 구분은 README.md 참고)
model = 'gpt-4o-mini'    # 가볍고 빠름·저렴, 일상 대화·간단 작업에 적합
# model = 'gpt-4o'       # 멀티모달 표준 모델, 품질·속도 균형이 좋음
# model = 'gpt-4.1-mini' # 긴 컨텍스트·코딩에 강한 경량 모델

system_prompt = '당신은 친절한 AI 도우미입니다.'
user_message = '인공지능을 한 문장으로 설명해줘.'

temperature = 0.7  # 바꿔보기 → 0.0 (정확·일관) / 1.5 (창의·다양)

response = client.chat.completions.create(
    model=model,
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message},
    ],
    # --- 응답 제어 파라미터 (3단계와 동일, 전달 위치만 다름) ---
    # 주의: 아래 파라미터는 '표준 모델'용. o-series/GPT-5 등 추론 모델은
    #       temperature 등을 미지원한다 (자세한 내용은 README.md 참고).
    temperature=temperature,  # 창의성 (0.0 정확 ~ 2.0 창의)
    max_tokens=100,           # 응답의 최대 토큰 수
    top_p=0.9,                # 확률 상위 토큰만 선택 (0.0 ~ 1.0)
    frequency_penalty=0.5,    # 같은 단어 반복 억제 (-2.0 ~ 2.0)
    presence_penalty=0.6,     # 새로운 주제 도입 장려 (-2.0 ~ 2.0)
)

print(f'[{model}, temperature={temperature}] 챗봇:', response.choices[0].message.content)
