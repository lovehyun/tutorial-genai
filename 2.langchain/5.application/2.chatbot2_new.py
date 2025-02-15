from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 환경 변수 로드
load_dotenv(dotenv_path='../.env')

# OpenAI 모델 설정 (gpt-3.5-turbo-instruct 대신 chat 모델 사용)
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# 체인 생성
chain = prompt | llm

print("Welcome to your AI Chatbot! What's on your mind?")
for _ in range(0, 3):
    human_input = input("You: ")
    ai_response = chain.invoke({"input": human_input})
    print(f"AI: {ai_response.content}")
