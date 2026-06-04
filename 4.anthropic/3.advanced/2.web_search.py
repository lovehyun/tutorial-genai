# pip install anthropic python-dotenv
#
# 고급 2: 서버 도구 — 웹 검색. 모델이 알아서 검색하고 결과를 반영해 답한다.
# 서버(Anthropic)에서 실행되므로 우리는 도구만 "선언"하면 된다(직접 실행 X).
# ★ 서버 도구는 별도 과금이 있을 수 있다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
    messages=[{"role": "user", "content": "오늘 기준 파이썬 최신 정식 버전이 뭐야? 간단히."}],
)

# 검색 과정 블록 + 최종 텍스트가 섞여 들어온다. 텍스트만 출력.
for block in resp.content:
    if block.type == "text":
        print(block.text)
