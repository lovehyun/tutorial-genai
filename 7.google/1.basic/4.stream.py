# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 스트리밍 응답
print("스트리밍 응답:")
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="머신러닝의 주요 알고리즘 5가지를 설명해주세요.",
):
    print(chunk.text, end="", flush=True)

print("\n\n스트리밍 완료!")
