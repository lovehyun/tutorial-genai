# pip install langchain-google-genai python-dotenv

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# LangChain Gemini 모델 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

# 간단한 호출
response = llm.invoke("인공지능의 3가지 핵심 기술을 설명해주세요.")
print(response.content)
