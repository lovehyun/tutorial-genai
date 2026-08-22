# pip install anthropic python-dotenv
#
# 고급 4: Batches API — 급하지 않은 대량 요청을 비동기로 처리(가격 50% 할인).
# 요청들을 모아 제출 → 완료까지 폴링 → 결과 수집.
# ★ 완료까지 보통 1시간 내(최대 24시간). 데모라도 시간이 걸린다.

import os
import time
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

texts = ["이 제품 최고예요!", "최악의 서비스, 다신 안 사요.", "그냥 평범해요."]

# 1) 여러 요청을 한 배치로 제출
batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id=f"item-{i}",
            params=MessageCreateParamsNonStreaming(
                model="claude-haiku-4-5",
                max_tokens=20,
                messages=[{"role": "user",
                           "content": f"한 단어로 감정 분류(긍정/부정/중립): {t}"}],
            ),
        )
        for i, t in enumerate(texts)
    ]
)
print("배치 생성:", batch.id, "|", batch.processing_status)

# 2) 완료까지 폴링
while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    print("  상태:", batch.processing_status)
    time.sleep(30)

# 3) 결과 수집
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        msg = result.result.message
        text = next((b.text for b in msg.content if b.type == "text"), "")
        print(f"{result.custom_id}: {text}")
