# pip install google-genai python-dotenv
#
# 함수 호출(Function Calling) — 모델이 "이 함수를 이 인자로 불러야겠다"고 판단하게 한다.
# `1.openai/7.function_calling`, `3.anthropic/2.tools/1.tool_use.py`와 같은 개념이다.
#
# 흐름: 도구 스키마 선언 → generate_content에 tools로 전달 → 모델이 직접 실행하지 않고
#       "이 함수를 이 인자로 불러라"라는 요청만 응답에 담아 돌려준다(실행은 항상 내 책임).

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트 1] 함수 스키마 선언 — 실제 코드가 아니라 "이런 함수가 있다"는 설명서다.
get_weather = types.FunctionDeclaration(
    name="get_weather",
    description="특정 도시의 현재 날씨를 조회한다",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string", "description": "도시 이름"}},
        "required": ["city"],
    },
)
tool = types.Tool(function_declarations=[get_weather])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="서울 날씨 어때?",
    config=types.GenerateContentConfig(tools=[tool]),
)

# [관전 포인트 2] 모델이 함수 호출을 요청하면 응답의 part에 function_call이 담겨 온다.
#   (함수가 필요 없는 질문이면 part.text에 그냥 답이 온다.)
part = response.candidates[0].content.parts[0]
if part.function_call:
    print("모델이 호출하려는 함수:", part.function_call.name)
    print("모델이 만든 인자:", dict(part.function_call.args))
else:
    print("함수 없이 일반 답변:", part.text)
