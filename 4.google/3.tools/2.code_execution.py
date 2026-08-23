# pip install google-genai python-dotenv
#
# 코드 실행(Code Execution) — 서버 내장 도구. 모델이 직접 파이썬 코드를 만들고,
# Google 서버의 샌드박스에서 실행한 뒤, 그 결과를 반영해 답한다(직접 실행 X, 도구만 선언).
# `3.anthropic/2.tools/4.code_execution.py`와 같은 개념 — 벤더별로 어떻게 다른지 비교해볼 것.
#
# 계산·통계처럼 모델이 '암산'으로 틀리기 쉬운 작업에 특히 유용하다.

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="1부터 50까지 숫자 중 소수(prime)가 몇 개인지 코드를 실행해서 정확히 세어줘.",
    config=types.GenerateContentConfig(tools=[types.Tool(code_execution=types.ToolCodeExecution())]),
)

# [관전 포인트] 응답 parts에 세 종류가 섞여 온다 — 설명(text), 모델이 짠 코드(executable_code),
#   그 코드를 실행한 결과(code_execution_result). 순서대로 출력해보면 사고 과정이 다 보인다.
for part in response.candidates[0].content.parts:
    if part.text:
        print("[설명]", part.text)
    if part.executable_code:
        print("[실행된 코드]\n", part.executable_code.code)
    if part.code_execution_result:
        print("[실행 결과]\n", part.code_execution_result.output)
