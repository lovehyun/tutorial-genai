from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# 메모리 설정
memory = ConversationBufferMemory(return_messages=True)

# 대화 체인 생성
chain = prompt | llm

# 대화 수행
def chat(message):
    response = chain.invoke({"input": message})
    return response.content

# 테스트
print(chat("Hello"))
print(chat("Can we talk about sports?"))
print(chat("What's a good sport to play outdoor?"))
