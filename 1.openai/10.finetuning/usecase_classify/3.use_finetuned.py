# Fine-tuning use-case [분류] - 3단계: 분류 모델 사용 + 베이스 비교
# FT_MODEL=ft:... python 3.use_finetuned.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

FT_MODEL = os.getenv('FT_MODEL')
if not FT_MODEL:
    raise SystemExit("FT_MODEL 환경변수에 파인튜닝 모델 ID(ft:...)를 넣어주세요.")

tests = ['송장번호 좀 알려주세요', '결제가 두 번 됐어요', '회원 탈퇴하고 싶어요', '주차 되나요?']

for t in tests:
    # 파인튜닝 모델 — system 없이도 '라벨만' 깔끔히 (학습으로 굳어짐)
    ft = client.chat.completions.create(
        model=FT_MODEL,
        messages=[{'role': 'user', 'content': t}],
    ).choices[0].message.content

    # 베이스 모델 — 같은 질문 (라벨만 시키지 않으면 설명을 덧붙이거나 형식이 흔들림)
    base = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': t}],
    ).choices[0].message.content

    print(f'\nQ: {t}')
    print(f'  [파인튜닝] {ft}')
    print(f'  [베이스]   {base[:60]}...')

# 정리:
#   - ft 모델은 '배송/환불/계정/결제/기타' 라벨만 일관되게 출력 → 그대로 라우팅에 사용.
#   - 대량 티켓 분류에서 mini-ft 가 비용·속도·일관성 우위. (학습 때 쓴 system 을 넣으면 더 안정적)
