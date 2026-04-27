import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 환경 변수 로드
load_dotenv()

# Claude 모델 초기화
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.7
)

# 프롬프트 (대화 히스토리 포함)
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 AI 어시스턴트입니다."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# LCEL 체인
chain = prompt | llm | StrOutputParser()

# 세션별 메모리 저장소
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# RunnableWithMessageHistory로 대화 메모리 관리
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "demo"}}

# 첫 번째 대화
response = conversation.invoke({"input": "인공지능이란 무엇인가요?"}, config=config)
print(response)

# 두 번째 대화 (이전 대화 컨텍스트 유지)
response = conversation.invoke({"input": "그것의 주요 발전 과정을 설명해주세요."}, config=config)
print(response)

# 세 번째 대화
response = conversation.invoke({"input": "앞으로의 전망은 어떤가요?"}, config=config)
print(response)
