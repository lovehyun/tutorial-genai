# pip install google-genai python-dotenv
#
# Grounding with Google Search — 모델이 답하기 전에 실시간으로 구글 검색을 해서,
# 학습 데이터 마감 이후의 최신 정보(오늘 날씨, 최근 뉴스 등)도 정확히 답한다.
# `1.openai/2.sdk/13.response_web_search.py`, `3.anthropic/2.tools/3.web_search.py`와
# 같은 개념 — Google은 자사 검색엔진을 그대로 붙인다는 게 차이.

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트 1] types.Tool(google_search=...) 하나만 추가하면 끝 — 검색 자체는 서버가 알아서 한다.
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="오늘 서울 날씨 어때?",
    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
)

print("답변:", response.text)

# [관전 포인트 2] grounding_metadata — 어떤 검색 결과를 근거로 답했는지 확인할 수 있다.
grounding = response.candidates[0].grounding_metadata
if grounding and grounding.grounding_chunks:
    print(f"\n참고한 출처 {len(grounding.grounding_chunks)}개:")
    for chunk in grounding.grounding_chunks:
        if chunk.web:
            print(f"  - {chunk.web.title}: {chunk.web.uri}")
