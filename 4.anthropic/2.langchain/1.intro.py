# pip install langchain anthropic python-dotenv

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",  # 최신 모델
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7,
    max_tokens=1000
)

# 간단한 프롬프트 실행
response = llm.invoke("인공지능의 미래에 대해 설명해주세요.")
print(response.content)
