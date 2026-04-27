# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai

# 환경 변수 로드
load_dotenv()

# Gemini 클라이언트 초기화
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 간단한 텍스트 생성
response = client.models.generate_content(
    model="gemini-2.5-flash",  # gemini-2.5-flash, gemini-2.5-pro
    contents="인공지능의 미래에 대해 간단히 설명해주세요.",
)

print(response.text)
