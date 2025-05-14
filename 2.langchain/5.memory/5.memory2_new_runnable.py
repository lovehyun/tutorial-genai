from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import Runnable

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

memory = ConversationBufferMemory(return_messages=True)

# 프롬프트
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

# 메모리 연결
chain_with_memory: Runnable = chain.with_config({"memory": memory})

def chat(message):
    return chain_with_memory.invoke({"input": message}).content
