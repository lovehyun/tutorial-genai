# pip install google-genai python-dotenv

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 멀티턴 대화 (Chat)
chat = client.chats.create(model="gemini-2.5-flash")

# 첫 번째 대화
response = chat.send_message("안녕하세요! 파이썬에 대해 알려주세요.")
print("1:", response.text)

# 두 번째 대화 (이전 컨텍스트 유지)
response = chat.send_message("그 중에서 가장 많이 쓰이는 분야는?")
print("2:", response.text)

# 세 번째 대화
response = chat.send_message("초보자가 시작하기 좋은 프로젝트를 추천해주세요.")
print("3:", response.text)
