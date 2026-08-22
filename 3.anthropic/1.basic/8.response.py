# pip install anthropic python-dotenv
#
# 8단계: 응답 객체 들여다보기.
# message 에는 텍스트 말고도 유용한 정보가 들어있다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"
messages = [{"role": "user", "content": "한국의 수도는?"}]

# (1) 호출 전에 입력 토큰 수를 미리 셀 수 있다 (과금 예측에 유용)
count = client.messages.count_tokens(model=MODEL, messages=messages)
print("예상 입력 토큰:", count.input_tokens)

# (2) 실제 호출
message = client.messages.create(model=MODEL, max_tokens=200, messages=messages)

# content: 블록 리스트. 블록마다 type 이 있다 (text / thinking / tool_use ...)
print("\ncontent 블록 수:", len(message.content))
for block in message.content:
    print("  - 블록 타입:", block.type)

# 텍스트만 안전하게 뽑기
text = next((b.text for b in message.content if b.type == "text"), "")
print("\n답변:", text)

# stop_reason: 왜 멈췄나 (end_turn=정상, max_tokens=길이초과로 잘림, tool_use=툴호출 ...)
print("stop_reason:", message.stop_reason)

# usage: 실제 사용 토큰 (과금 기준)
print("입력 토큰:", message.usage.input_tokens)
print("출력 토큰:", message.usage.output_tokens)
