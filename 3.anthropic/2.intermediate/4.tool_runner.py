# pip install anthropic python-dotenv
#
# 중급 4: tool runner (beta) — 도구 호출 루프를 SDK 가 자동으로 돌려준다.
# 3.tool_use.py 의 수동 루프(요청→실행→결과→재호출)를 @beta_tool + tool_runner 로 간단히.

import os
import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 함수 시그니처 + docstring 으로 도구 스키마가 자동 생성된다.
@beta_tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 반환한다.

    Args:
        city: 도시 이름.
    """
    return f"{city}: 맑음, 22도"

# tool_runner 가 호출→실행→결과 전달→재호출 루프를 알아서 돈다.
runner = client.beta.messages.tool_runner(
    model="claude-sonnet-4-6",
    max_tokens=500,
    tools=[get_weather],
    messages=[{"role": "user", "content": "서울이랑 부산 날씨 둘 다 알려줘."}],
)

# 각 반복마다 메시지가 나온다. 마지막 메시지가 최종 답.
for message in runner:
    for block in message.content:
        if block.type == "text":
            print(block.text)
