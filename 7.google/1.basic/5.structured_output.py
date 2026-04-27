# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# Pydantic 모델로 구조화된 출력 정의
class BookRecommendation(BaseModel):
    title: str
    author: str
    genre: str
    reason: str


class BookList(BaseModel):
    books: list[BookRecommendation]


# 구조화된 출력 요청
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="인공지능에 관한 추천 도서 3권을 알려주세요.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BookList,
    ),
)

# JSON 파싱
import json
data = json.loads(response.text)
for book in data["books"]:
    print(f"  {book['title']} — {book['author']} ({book['genre']})")
    print(f"    추천 이유: {book['reason']}\n")
