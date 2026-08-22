# pip install anthropic python-dotenv
#
# 중급 3: 도구 호출(tool use) — 모델이 직접 못 하는 일을 "도구"에 위임한다.
# 흐름: 도구 정의 → 모델이 tool_use 로 호출 요청 → 우리가 실행 → tool_result 로 돌려줌 → 최종 답.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 1) 도구 정의 (이름 / 설명 / 입력 스키마)
tools = [{
    "name": "get_weather",
    "description": "도시의 현재 날씨를 반환한다.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "도시 이름"}},
        "required": ["city"],
    },
}]

# 실제 도구 구현 (여기선 가짜 데이터)
def get_weather(city):
    return f"{city}: 맑음, 22도"

messages = [{"role": "user", "content": "서울 날씨 어때?"}]

# 2) 1차 호출 — 모델이 도구를 쓰겠다고 하면 stop_reason == "tool_use"
resp = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=500, tools=tools, messages=messages)
print("stop_reason:", resp.stop_reason)

# 3) 모델 응답(도구 호출 포함)을 기록에 추가하고, 도구를 실행해 결과를 돌려준다
messages.append({"role": "assistant", "content": resp.content})
tool_results = []
for block in resp.content:
    if block.type == "tool_use":
        result = get_weather(**block.input)          # 모델이 채워준 인자로 실행
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,                  # 어떤 호출에 대한 결과인지 매칭
            "content": result,
        })
messages.append({"role": "user", "content": tool_results})

# 4) 도구 결과를 받은 뒤 최종 답변
final = client.messages.create(
    model="claude-sonnet-4-6", max_tokens=500, tools=tools, messages=messages)
print(next(b.text for b in final.content if b.type == "text"))
