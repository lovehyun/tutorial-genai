# pip install anthropic python-dotenv
#
# 2단계: system 프롬프트 — 모델의 역할/말투를 정한다.
# ★ 중요: Anthropic API 에서 system 은 messages 안의 role 이 아니라 top-level 파라미터다.
#         (OpenAI 처럼 messages 에 {"role":"system"} 으로 넣지 않는다)

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    system="너는 해적처럼 말하는 챗봇이다. 모든 답을 해적 말투로 한다.",  # ← top-level
    messages=[
        {"role": "user", "content": "오늘 날씨가 좋네."}
    ],
)

print(message.content[0].text)
