# pip install google-genai python-dotenv
#
# Grounding with Google Maps — 다른 어떤 벤더에도 없는 Google만의 기능.
# 실제 구글 지도 데이터(평점·리뷰·영업 정보 등)를 근거로 장소를 추천/설명하게 한다.
# `1.google_search.py`가 "웹 전체"를 근거로 쓴다면, 이건 "지도/장소 데이터"에 특화된 버전이다.

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트] types.Tool(google_maps=...) — 실제 매장 평점·리뷰 수까지 반영된 답이 온다.
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="서울 강남역 근처 맛있는 파스타 맛집 하나만 추천해줘.",
    config=types.GenerateContentConfig(tools=[types.Tool(google_maps=types.GoogleMaps())]),
)

print(response.text)

# 참고: 다른 벤더(OpenAI, Anthropic)에는 지도 데이터 기반 그라운딩 도구가 없다 —
#       위치 기반 추천/검증이 필요한 앱(맛집 추천, 근처 시설 안내 등)이라면 Gemini가 유리한 지점이다.
