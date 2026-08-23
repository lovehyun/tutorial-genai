# Fine-tuning use-case [구조화 추출] - 1단계: 학습 데이터
# pip install openai python-dotenv
#
# 대표 use-case: 자유 형식 텍스트 → '고정 JSON 스키마'로 추출 (인보이스/주문/이력서 등).
# 포인트: assistant 응답이 '항상 같은 키의 JSON' → 복잡한 포맷도 일관되게 굳힌다.

import json

SYSTEM = ('주문 메모에서 정보를 추출해 JSON 으로만 출력한다. '
          '키는 정확히 item, quantity, price, date 네 개. 값이 없으면 null.')

# (메모, 정답 JSON) — assistant 는 JSON 문자열
pairs = [
    ("어제 사과 3개 4500원에 샀어요 (2026-06-01)",
     {"item": "사과", "quantity": 3, "price": 4500, "date": "2026-06-01"}),
    ("6/2 우유 2팩 3200원",
     {"item": "우유", "quantity": 2, "price": 3200, "date": "2026-06-02"}),
    ("연필 한 자루 800원 받음",
     {"item": "연필", "quantity": 1, "price": 800, "date": None}),
    ("2026-06-03 노트 5권 합 6000원",
     {"item": "노트", "quantity": 5, "price": 6000, "date": "2026-06-03"}),
    ("바나나 한 송이 (가격 미정)",
     {"item": "바나나", "quantity": 1, "price": None, "date": None}),
    ("6월 4일에 커피 4잔 18000원 결제",
     {"item": "커피", "quantity": 4, "price": 18000, "date": "2026-06-04"}),
    ("물 12병 묶음 9600원 06-05",
     {"item": "물", "quantity": 12, "price": 9600, "date": "2026-06-05"}),
    ("샤프심 2개 1400원",
     {"item": "샤프심", "quantity": 2, "price": 1400, "date": None}),
]

with open("train.jsonl", "w", encoding="utf-8") as f:
    for memo, obj in pairs:
        f.write(json.dumps({"messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": memo},
            {"role": "assistant", "content": json.dumps(obj, ensure_ascii=False)},
        ]}, ensure_ascii=False) + "\n")

print(f"train.jsonl 생성 ({len(pairs)}개)  → 2.create_job.py")
