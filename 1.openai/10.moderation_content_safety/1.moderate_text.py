# Moderation - 1단계: 텍스트 안전성 검사 (무료)
# pip install openai python-dotenv
#
# Moderation API 는 입력이 OpenAI 정책(폭력/혐오/자해/성적 등)에 걸리는지 검사한다. 무료.
# 보통 사용자 입력을 LLM 에 보내기 '전에' 걸러내는 안전장치로 쓴다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

texts = [
    '오늘 날씨 정말 좋다! 산책 가야지.',
    '나는 그 사람을 해치고 싶어.',          # 위반 예시
]

for t in texts:
    r = client.moderations.create(model='omni-moderation-latest', input=t)
    result = r.results[0]
    print(f'\n입력: {t}')
    print(f'  차단 대상(flagged): {result.flagged}')
    if result.flagged:
        # 어떤 카테고리가 True 인지
        cats = [c for c, v in result.categories.model_dump().items() if v]
        print(f'  걸린 카테고리: {cats}')
