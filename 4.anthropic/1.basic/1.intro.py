# pip install anthropic

import os
import anthropic
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Anthropic 클라이언트 초기화
client = anthropic.Anthropic(
    api_key=api_key
)

# 간단한 메시지 보내기
message = client.messages.create(
    model="claude-3-7-sonnet-20250219",  # 최신 모델, 사용 가능한 모델은 달라질 수 있음
    max_tokens=1000,
    temperature=0.7,
    messages=[
        {"role": "user", "content": "안녕하세요! Python으로 간단한 계산기를 만들고 싶은데 도와주실 수 있나요?"}
    ]
)

# 응답 출력
# print(message.content)
print(message.content[0].text)
