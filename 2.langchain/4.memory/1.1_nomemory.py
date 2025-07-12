from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# prompt = ChatPromptTemplate.from_messages([
#     ChatMessagePromptTemplate.from_template(role="human", template="{input}")
# ])
# 참고: LangChain에서 "human"과 "user"는 같은 역할로 간주되며, "ai"와 "assistant"도 동일하게 취급됩니다.


# 대화 체인 생성 - 메모리가 연결되지 않음
chain = prompt | llm

# 대화 수행
def chat(message):
    response = chain.invoke({"input": message})
    return response.content

# 테스트
print(chat("Hello"))
print(chat("Can we talk about sports?"))
print(chat("What's a good sport to play outdoor?"))
