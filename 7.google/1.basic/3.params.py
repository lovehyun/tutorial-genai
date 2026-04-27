# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 파라미터 설정을 통한 생성 제어
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="창의적인 SF 소설의 첫 문단을 작성해주세요.",
    config=types.GenerateContentConfig(
        temperature=0.9,       # 창의성 (0.0~2.0)
        top_p=0.95,            # 누적 확률
        top_k=40,              # 후보 토큰 수
        max_output_tokens=500, # 최대 출력 토큰
    ),
)

print(response.text)
print(f"\n사용 토큰: {response.usage_metadata}")
