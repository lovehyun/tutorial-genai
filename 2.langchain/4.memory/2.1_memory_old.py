from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정 - 모델명 확인
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 메모리 설정
memory = ConversationBufferMemory()

# ConversationChain 생성 - v0.2.7부터 사용 중단(deprecated)
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 대화 수행
def chat(message):
    # conversation.predict 사용
    response = conversation.predict(input=message)
    return response


# 테스트
print(chat("Hello"))
print(chat("Can we talk about sports?"))
print(chat("What's a good sport to play outdoor?"))
