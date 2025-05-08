import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 대화 메모리 체인 생성
conversation = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory(),
    verbose=True
)

# 첫 번째 대화
response = conversation.invoke({"input": "인공지능이란 무엇인가요?"})
print(response["response"])

# 두 번째 대화 (이전 대화 컨텍스트 유지)
response = conversation.invoke({"input": "그것의 주요 발전 과정을 설명해주세요."})
print(response["response"])

# 세 번째 대화
response = conversation.invoke({"input": "앞으로의 전망은 어떤가요?"})
print(response["response"])
