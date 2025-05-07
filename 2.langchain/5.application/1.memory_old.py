from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# OpenAI 채팅 모델 설정 (대화형 모델이므로 ChatOpenAI 사용)
llm = ChatOpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

# 최신 LangChain 실행 방식 적용
conversation = ConversationChain(llm=llm, verbose=True)

# 대화 수행
conversation.invoke({"input": "Hello"})
conversation.invoke({"input": "Can we talk about sports?"})
response = conversation.invoke({"input": "What's a good sport to play outdoor?"})

# 결과 출력
print(response["response"])
