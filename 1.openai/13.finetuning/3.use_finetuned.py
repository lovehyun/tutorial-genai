# Fine-tuning - 3단계(실용): 파인튜닝된 모델 사용 + 베이스 모델과 비교
# pip install openai python-dotenv
#
# 2.create_job 의 결과 모델 ID(ft:gpt-4o-mini-...)를 FT_MODEL 환경변수로 넣고 실행.
#   예) FT_MODEL=ft:gpt-4o-mini-2024-07-18:org::abc123 python 3.use_finetuned.py
#
# 포인트: 파인튜닝 모델은 학습한 '톤·형식'을 system 프롬프트 없이도(혹은 짧게) 재현한다.
#         같은 질문을 베이스 모델과 비교해 차이를 본다.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

FT_MODEL = os.getenv('FT_MODEL')   # 2단계에서 얻은 ft:... 모델 ID
if not FT_MODEL:
    raise SystemExit("FT_MODEL 환경변수에 파인튜닝 모델 ID(ft:...)를 넣어주세요.")

questions = ['반품하고 싶어요.', '적립금은 얼마까지 쌓여요?']

for q in questions:
    # 파인튜닝 모델 — 짧은 system(또는 없이)으로도 학습된 간결 톤 재현
    ft = client.chat.completions.create(
        model=FT_MODEL,
        messages=[{'role': 'user', 'content': q}],
    ).choices[0].message.content

    # 베이스 모델 — 같은 질문 (보통 더 길고 톤이 들쭉날쭉)
    base = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': q}],
    ).choices[0].message.content

    print(f'\nQ: {q}')
    print(f'  [파인튜닝] {ft}')
    print(f'  [베이스]   {base}')

# 정리:
#   - 파인튜닝 모델은 '한 문장 존댓말 핵심만' 톤을 프롬프트 없이도 일관되게 낸다(학습으로 굳힘).
#   - 같은 걸 프롬프트로 매번 지시할 수도 있지만, 파인튜닝은 프롬프트를 짧게/일관되게 만든다.
#   - 새 '지식'이 필요하면 파인튜닝이 아니라 RAG(7.rag) 임을 기억.
