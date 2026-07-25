# Fine-tuning use-case [분류] - 1단계: 학습 데이터
# pip install openai python-dotenv
#
# 대표 use-case: 문의를 고정 카테고리로 '분류'(티켓 라우팅/인텐트).
# 포인트: assistant 응답이 '라벨 한 단어'뿐 → 모델이 깔끔한 분류기를 학습한다.
#   (대량 분류는 작은 ft 모델이 큰 모델 프롬프팅보다 싸고 빠르고 일관적)

import json

SYSTEM = "고객 문의를 다음 중 하나로 분류한다: 배송, 환불, 계정, 결제, 기타. 라벨 한 단어만 출력한다."

pairs = [
    ("택배가 아직 안 왔어요", "배송"),
    ("언제 도착하나요?", "배송"),
    ("배송지를 바꾸고 싶어요", "배송"),
    ("주문 취소하고 돈 돌려주세요", "환불"),
    ("환불은 며칠 걸려요?", "환불"),
    ("반품하면 환불되나요?", "환불"),
    ("비밀번호를 잊었어요", "계정"),
    ("로그인이 안 됩니다", "계정"),
    ("이메일 주소를 변경하려면?", "계정"),
    ("카드 결제가 안 돼요", "결제"),
    ("쿠폰이 적용이 안 돼요", "결제"),
    ("결제 영수증 주세요", "결제"),
    ("영업시간이 어떻게 되나요?", "기타"),
    ("매장 위치 알려주세요", "기타"),
    ("선물 포장 되나요?", "기타"),
]

with open("train.jsonl", "w", encoding="utf-8") as f:
    for user, label in pairs:
        f.write(json.dumps({"messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": label},
        ]}, ensure_ascii=False) + "\n")

print(f"train.jsonl 생성 ({len(pairs)}개)  → 2.create_job.py")
