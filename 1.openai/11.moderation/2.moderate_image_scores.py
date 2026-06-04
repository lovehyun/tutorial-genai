# Moderation - 2단계: 이미지+텍스트 검사 + 카테고리 '점수' 보기
# pip install openai python-dotenv
#
# omni-moderation-latest 는 멀티모달 → 이미지도 검사한다.
# flagged(차단여부) 외에 category_scores(0~1)를 보면 '얼마나 위험한지' 정도를 알 수 있다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 텍스트 + 이미지 동시 검사 (이미지 URL)
r = client.moderations.create(
    model='omni-moderation-latest',
    input=[
        {'type': 'text', 'text': '이 이미지를 검토해줘.'},
        {'type': 'image_url',
         'image_url': {'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/640px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg'}},
    ],
)
result = r.results[0]
print('차단 대상(flagged):', result.flagged)

# 카테고리별 점수 상위 5개 (낮을수록 안전)
scores = result.category_scores.model_dump()
top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
print('상위 카테고리 점수:')
for cat, score in top:
    print(f'  {cat:30s} {score:.5f}')
