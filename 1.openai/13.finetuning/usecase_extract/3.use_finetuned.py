# Fine-tuning use-case [구조화 추출] - 3단계: 추출 모델 사용 (JSON 파싱)
# FT_MODEL=ft:... python 3.use_finetuned.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

FT_MODEL = os.getenv('FT_MODEL')
if not FT_MODEL:
    raise SystemExit("FT_MODEL 환경변수에 파인튜닝 모델 ID(ft:...)를 넣어주세요.")

memos = [
    '6/6 초콜릿 3개 7500원 샀음',
    '지우개 한 개 (500원)',
    '딸기 2팩 2026-06-07 결제, 금액은 나중에',
]

for memo in memos:
    raw = client.chat.completions.create(
        model=FT_MODEL,
        messages=[{'role': 'user', 'content': memo}],
    ).choices[0].message.content

    print(f'\n메모: {memo}')
    print(f'  출력: {raw}')
    # 학습으로 'JSON만' 내도록 굳었으므로 바로 파싱해서 쓸 수 있다
    try:
        obj = json.loads(raw)
        print(f'  파싱: item={obj.get("item")}, qty={obj.get("quantity")}, '
              f'price={obj.get("price")}, date={obj.get("date")}')
    except json.JSONDecodeError:
        print('  (JSON 파싱 실패 — 데이터가 적거나 일관성이 부족하면 발생. 예시를 늘리세요)')

# 정리:
#   - ft 모델은 '항상 같은 키의 JSON'을 내도록 학습 → 후처리 파이프라인이 단순해진다.
#   - 더 강하게 보장하려면 with_structured_output / response_format(json_schema) 과 병행 가능.
