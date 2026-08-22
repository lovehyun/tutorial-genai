# pip install anthropic python-dotenv
#
# 고급 3: 서버 도구 — 코드 실행. 모델이 샌드박스에서 파이썬 코드를 돌려 계산/분석한다.
# 역시 서버에서 실행되므로 도구만 선언하면 된다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
    messages=[{"role": "user", "content": "1부터 100까지 소수의 개수를 코드를 실행해서 구해줘."}],
)

for block in resp.content:
    if block.type == "text":
        print(block.text)
