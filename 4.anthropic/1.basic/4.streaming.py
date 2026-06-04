# pip install anthropic python-dotenv
#
# 4단계: 스트리밍 — 답을 한 번에 받지 않고 생성되는 대로 흘려 받는다.
# 긴 답변에서 체감 속도가 빨라지고, 타임아웃 위험도 줄어든다.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=500,
    messages=[{"role": "user", "content": "바다에 대한 짧은 시를 써줘."}],
) as stream:
    # text_stream 은 텍스트 조각만 순서대로 내준다
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # 스트림이 끝난 뒤 완성된 메시지 객체가 필요하면 get_final_message()
    final = stream.get_final_message()

print()
print("\n[사용 토큰] 출력:", final.usage.output_tokens)
