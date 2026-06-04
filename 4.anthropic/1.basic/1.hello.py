# pip install anthropic python-dotenv
#
# 1단계: 가장 단순한 호출 한 번.
# 빠르고 저렴한 Haiku 로 첫 호출을 해본다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# messages.create 가 기본. model / max_tokens / messages 3개가 필수다.
message = client.messages.create(
    model="claude-haiku-4-5",   # 가장 빠르고 저렴 — 연습/간단한 작업에 적합
    max_tokens=300,
    messages=[
        {"role": "user", "content": "안녕! 한 문장으로 자기소개 해줘."}
    ],
)

# 응답은 content(블록 리스트)에 담긴다. 지금은 텍스트 한 블록뿐이라 [0].text 로 충분.
print(message.content[0].text)
